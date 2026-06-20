"""Translation Tab - VDT<->ODOT code mapping review and override UI."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Optional, Dict, List

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QBrush
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QTableWidget,
    QTableWidgetItem, QComboBox, QLineEdit, QPushButton, QLabel,
    QMessageBox, QFileDialog, QHeaderView,
)

from app.services import translation_map as tm
from app.ui.translation_review_pane import TranslationReviewPane

CONFIDENCE_COLORS = {
    "exact":      QColor(200, 240, 200),  # green
    "best-guess": QColor(255, 245, 180),  # yellow
    "unmatched":  QColor(255, 200, 200),  # red
    "manual":     QColor(200, 220, 255),  # blue
}

COLUMNS = [
    "VDT Code", "VDT Type", "VDT Desc",
    "Confidence",
    "ODOT Code", "ODOT Type", "ODOT Desc",
    "Override",
]


class TranslationTab(QWidget):
    """Tab widget for reviewing and overriding VDT<->ODOT translation map entries."""

    map_modified = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._map_data: Dict = {"entries": []}
        self._build_ui()
        self.refresh_map()

    # ---------- UI construction ----------

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)

        # Filter bar
        filter_bar = QHBoxLayout()
        filter_bar.addWidget(QLabel("Confidence:"))
        self.confidence_filter = QComboBox()
        self.confidence_filter.addItems(["All", "exact", "best-guess", "unmatched", "manual"])
        self.confidence_filter.currentTextChanged.connect(self._apply_filters)
        filter_bar.addWidget(self.confidence_filter)

        filter_bar.addWidget(QLabel("Type:"))
        self.type_filter = QComboBox()
        self.type_filter.addItems(["All", "Point", "Linework", "Symbol"])
        self.type_filter.currentTextChanged.connect(self._apply_filters)
        filter_bar.addWidget(self.type_filter)

        filter_bar.addWidget(QLabel("Search:"))
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("VDT or ODOT code...")
        self.search_box.textChanged.connect(self._apply_filters)
        filter_bar.addWidget(self.search_box)

        filter_bar.addStretch(1)

        # Toolbar
        self.reseed_btn = QPushButton("Reseed Map...")
        self.reseed_btn.clicked.connect(self._on_reseed)
        filter_bar.addWidget(self.reseed_btn)

        self.export_btn = QPushButton("Export Review CSV")
        self.export_btn.clicked.connect(self._on_export_csv)
        filter_bar.addWidget(self.export_btn)

        self.save_btn = QPushButton("Save Overrides")
        self.save_btn.clicked.connect(self._on_save)
        filter_bar.addWidget(self.save_btn)

        root.addLayout(filter_bar)

        # Splitter: table | review pane
        splitter = QSplitter(Qt.Horizontal)

        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        splitter.addWidget(self.table)

        self.review_pane = TranslationReviewPane()
        self.review_pane.entry_modified.connect(self._on_entry_modified)
        splitter.addWidget(self.review_pane)

        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        root.addWidget(splitter)

    # ---------- Data load / save ----------

    def refresh_map(self) -> None:
        """Reload translation_map.json from disk and repopulate the table."""
        try:
            self._map_data = tm.load()
        except FileNotFoundError:
            QMessageBox.warning(
                self, "Translation Map Missing",
                "app/data/translation_map.json not found.\n"
                "Run reseed_translation_map.bat or apply Phase 1 first."
            )
            return
        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Failed to load translation map:\n{e}")
            return
        self._populate_table(self._map_data["entries"])

    def _populate_table(self, entries: List[Dict]) -> None:
        self.table.setRowCount(0)
        for entry in entries:
            self._append_entry_row(entry)

    def _append_entry_row(self, entry: Dict) -> None:
        row = self.table.rowCount()
        self.table.insertRow(row)

        vdt = entry.get("vdt") or {}
        odot = entry.get("odot") or {}
        confidence = entry.get("confidence", "unmatched")
        override = "Yes" if entry.get("user_override") else ""

        values = [
            vdt.get("code", ""), vdt.get("type", ""), vdt.get("description", ""),
            confidence,
            odot.get("code", ""), odot.get("type", ""), odot.get("description", ""),
            override,
        ]
        color = CONFIDENCE_COLORS.get(confidence)
        for col, val in enumerate(values):
            item = QTableWidgetItem(str(val))
            if color is not None:
                item.setBackground(QBrush(color))
            item.setData(Qt.UserRole, entry.get("id"))
            self.table.setItem(row, col, item)

    # ---------- Filters ----------

    def _apply_filters(self) -> None:
        confidence = self.confidence_filter.currentText()
        type_filter = self.type_filter.currentText()
        search = self.search_box.text().strip().lower()

        for row in range(self.table.rowCount()):
            visible = True
            if confidence != "All":
                if self.table.item(row, 3).text() != confidence:
                    visible = False
            if visible and type_filter != "All":
                vdt_type = self.table.item(row, 1).text()
                odot_type = self.table.item(row, 5).text()
                if type_filter not in (vdt_type, odot_type):
                    visible = False
            if visible and search:
                vdt_code = self.table.item(row, 0).text().lower()
                odot_code = self.table.item(row, 4).text().lower()
                if search not in vdt_code and search not in odot_code:
                    visible = False
            self.table.setRowHidden(row, not visible)

    # ---------- Selection / review pane ----------

    def _on_selection_changed(self) -> None:
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            self.review_pane.clear_entry()
            return
        entry_id = self.table.item(rows[0].row(), 0).data(Qt.UserRole)
        entry = self._find_entry(entry_id)
        if entry is not None:
            self.review_pane.load_entry(entry, self._all_odot_codes())

    def _find_entry(self, entry_id: str) -> Optional[Dict]:
        for e in self._map_data["entries"]:
            if e.get("id") == entry_id:
                return e
        return None

    def _all_odot_codes(self) -> List[str]:
        codes = set()
        for e in self._map_data["entries"]:
            if e.get("odot"):
                codes.add(e["odot"]["code"])
        return sorted(codes)

    def _on_entry_modified(self, entry_id: str) -> None:
        self.refresh_map()  # cheap full reload for now
        self.map_modified.emit()

    # ---------- Toolbar actions ----------

    def _on_reseed(self) -> None:
        resp = QMessageBox.question(
            self, "Reseed Translation Map",
            "This will OVERWRITE app/data/translation_map.json and "
            "DISCARD all manual overrides.\n\nContinue?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if resp != QMessageBox.Yes:
            return
        from app.services import seed_translation_map as seeder
        try:
            seeder.seed(force=True)
        except Exception as e:
            QMessageBox.critical(self, "Reseed Failed", str(e))
            return
        self.refresh_map()
        QMessageBox.information(self, "Reseed Complete", "Translation map regenerated.")

    def _on_export_csv(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Review CSV", "translation_map_review.csv", "CSV (*.csv)"
        )
        if not path:
            return
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(COLUMNS)
            for row in range(self.table.rowCount()):
                if self.table.isRowHidden(row):
                    continue
                writer.writerow([
                    self.table.item(row, c).text() for c in range(len(COLUMNS))
                ])
        QMessageBox.information(self, "Export Complete", f"Wrote {path}")

    def _on_save(self) -> None:
        try:
            tm.save(self._map_data)
        except Exception as e:
            QMessageBox.critical(self, "Save Failed", str(e))
            return
        QMessageBox.information(self, "Saved", "Overrides written to translation_map.json")
