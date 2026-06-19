"""Modified Data tab - per-row description selection + PNEZD export."""
import logging
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QComboBox, QLineEdit, QHeaderView, QLabel,
    QFileDialog, QMessageBox,
)

from app.services.csv_exporter import write_pnezd

log = logging.getLogger("robs_code_wizard")

COLUMNS = ["P", "N", "E", "Z", "Original D", "Suggestion",
           "Use", "Custom D", "Final D"]
COL_P, COL_N, COL_E, COL_Z = 0, 1, 2, 3
COL_ORIG, COL_SUG, COL_USE, COL_CUSTOM, COL_FINAL = 4, 5, 6, 7, 8

USE_OPTIONS = ["Original", "Suggestion", "Custom"]


def _p_sort_key(row):
    """Sort key: numeric P where possible, else lexical."""
    try:
        return (0, float(row.get("P", 0) or 0))
    except (TypeError, ValueError):
        return (1, str(row.get("P", "")))


class ModifiedDataTab(QWidget):
    """Edit descriptions per row, preview Final D, and export PNEZD CSV."""

    def __init__(self, main_window):
        super().__init__()
        self.mw = main_window
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        bar = QHBoxLayout()
        bar.addWidget(QLabel("Modify descriptions per row, then:"))
        bar.addStretch(1)
        self.export_btn = QPushButton("Export Updated CSV...")
        self.export_btn.clicked.connect(self.on_export_updated)
        self.export_btn.setEnabled(False)
        bar.addWidget(self.export_btn)
        layout.addLayout(bar)

        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

    # -----------------------------------------------------------------
    # Refresh from MainWindow data
    # -----------------------------------------------------------------
    def refresh_from_parent(self):
        rows = list(self.mw.rows)
        suggestions = list(self.mw.suggestions) if self.mw.suggestions else [""] * len(rows)
        results = list(self.mw.results) if self.mw.results else [{"valid": True, "issues": []}] * len(rows)

        # Pair rows with their metadata and sort by P
        indexed = list(zip(rows, suggestions, results))
        indexed.sort(key=lambda t: _p_sort_key(t[0]))

        self.table.setSortingEnabled(False)
        self.table.setUpdatesEnabled(False)
        try:
            self.table.setRowCount(len(indexed))
            for i, (row, sug, res) in enumerate(indexed):
                self._populate_row(i, row, sug or "", res)
        finally:
            self.table.setUpdatesEnabled(True)
            self.table.setSortingEnabled(False)
            self.table.viewport().update()
        self.table.resizeColumnsToContents()
        self.export_btn.setEnabled(bool(indexed))

    def _populate_row(self, i, row, suggestion, result):
        original_d = str(row.get("D", ""))

        # Read-only cells
        self._set_ro(i, COL_P, str(row.get("P", "")))
        self._set_ro(i, COL_N, str(row.get("N", "")))
        self._set_ro(i, COL_E, str(row.get("E", "")))
        self._set_ro(i, COL_Z, str(row.get("Z", "")))
        self._set_ro(i, COL_ORIG, original_d)
        self._set_ro(i, COL_SUG, str(suggestion))

        # Use combo
        combo = QComboBox()
        combo.addItems(USE_OPTIONS)
        combo.setCurrentIndex(0)  # default Original
        combo.currentIndexChanged.connect(lambda _idx, r=i: self._on_use_changed(r))
        self.table.setCellWidget(i, COL_USE, combo)

        # Custom D editor
        custom_edit = QLineEdit()
        custom_edit.setPlaceholderText("(used when Use=Custom)")
        custom_edit.textChanged.connect(lambda _txt, r=i: self._on_custom_changed(r))
        self.table.setCellWidget(i, COL_CUSTOM, custom_edit)

        # Final D (read-only preview)
        self._set_ro(i, COL_FINAL, original_d)

        # Color the row
        self._color_row(i, row, result)

    def _set_ro(self, i, c, text):
        item = QTableWidgetItem(text)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(i, c, item)

    def _color_row(self, i, row, result):
        zero_elev = False
        try:
            zero_elev = float(row.get("Z", 0) or 0) == 0.0
        except (TypeError, ValueError):
            pass
        bad_code = not result.get("valid", True)
        color = None
        if bad_code:
            color = QColor("#ff6b6b")
        elif zero_elev:
            color = QColor("#fff3a0")
        if color:
            for c in range(self.table.columnCount()):
                cell = self.table.item(i, c)
                if cell:
                    cell.setBackground(color)

    # -----------------------------------------------------------------
    # Cell handlers
    # -----------------------------------------------------------------
    def _on_use_changed(self, row):
        self._update_final(row)

    def _on_custom_changed(self, row):
        combo = self.table.cellWidget(row, COL_USE)
        if combo and combo.currentText() == "Custom":
            self._update_final(row)

    def _update_final(self, row):
        combo = self.table.cellWidget(row, COL_USE)
        custom_edit = self.table.cellWidget(row, COL_CUSTOM)
        if combo is None:
            return
        choice = combo.currentText()
        if choice == "Original":
            final = self._cell_text(row, COL_ORIG)
        elif choice == "Suggestion":
            final = self._cell_text(row, COL_SUG)
        elif choice == "Custom":
            final = custom_edit.text() if custom_edit else ""
        else:
            final = self._cell_text(row, COL_ORIG)
        cell = self.table.item(row, COL_FINAL)
        if cell:
            cell.setText(final)

    def _cell_text(self, row, col):
        cell = self.table.item(row, col)
        return cell.text() if cell else ""

    # -----------------------------------------------------------------
    # Export
    # -----------------------------------------------------------------
    def on_export_updated(self):
        try:
            if self.table.rowCount() == 0:
                QMessageBox.information(self, "Export Updated CSV",
                                        "No data to export.")
                return

            default_name = "modified.csv"
            if self.mw.source_path:
                stem = Path(self.mw.source_path).stem
                default_name = f"{stem}_modified.csv"

            path, _ = QFileDialog.getSaveFileName(
                self, "Export Updated PNEZD",
                default_name,
                "CSV (*.csv);;Text (*.txt);;All files (*.*)",
            )
            if not path:
                return

            rows_out = self._collect_rows_for_export()
            write_pnezd(rows_out, path)
            log.info("Exported updated PNEZD: %s rows -> %s", len(rows_out), path)
            QMessageBox.information(
                self, "Export Updated CSV",
                f"Wrote {len(rows_out)} rows to:\n{path}",
            )
        except Exception as exc:
            log.exception("Export Updated CSV failed: %s", exc)
            QMessageBox.critical(
                self, "Export failed",
                f"{exc}\n\nSee log for details.",
            )

    def _collect_rows_for_export(self):
        """Build the list of dicts that csv_exporter.write_pnezd wants."""
        rows = []
        for i in range(self.table.rowCount()):
            self._update_final(i)  # ensure Final D is current
            rows.append({
                "P": self._cell_text(i, COL_P),
                "N": self._cell_text(i, COL_N),
                "E": self._cell_text(i, COL_E),
                "Z": self._cell_text(i, COL_Z),
                "D": self._cell_text(i, COL_FINAL),
            })
        return rows
