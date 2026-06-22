"""Translation Tab - v0.5.1 rebuild.

UX changes from v0.4.3:
    - Auto-detected source dialect from parent.codeset.name (read-only label)
    - Single "Translate Loaded Rows" button (no Source/Target friction)
    - Combined filter: search box + confidence checkboxes
    - Table split into "Used in loaded file" + "Other catalog codes" sections
    - Usage indicator + Count column
    - Dirty indicator for unsaved overrides
    - Why column with human-readable match-basis
    - Bottom review pane (wide, not cramped)
    - Bulk "Accept all Best-Guess in view" action
    - Manual edits to any entry supported
"""
from __future__ import annotations

import csv
from typing import Optional, Dict, List

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QBrush, QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QTableWidget,
    QTableWidgetItem, QComboBox, QLineEdit, QPushButton, QLabel,
    QMessageBox, QFileDialog, QHeaderView, QGroupBox, QCheckBox,
    QFrame,
)

from app.services import translation_map as tm
from app.services.usage_analyzer import analyze_used_codes, build_usage_summary
from app.services.match_basis_descriptor import describe, short_label
from app.ui.translation_review_pane import TranslationReviewPane

CONFIDENCE_COLORS = {
    "exact":      QColor(200, 240, 200),
    "best-guess": QColor(255, 245, 180),
    "unmatched":  QColor(255, 200, 200),
    "manual":     QColor(200, 220, 255),
}

COLUMNS = [
    "\u25CF", "Used", "Count",
    "VDT Code", "VDT Type", "VDT Desc",
    "ODOT Code", "ODOT Type", "ODOT Desc",
    "Confidence", "Why",
]


class TranslationTab(QWidget):
    map_modified = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._parent_main = parent
        self._map_data: Dict = {"entries": []}
        self._used_counts: Dict[str, int] = {}
        self._dirty_entry_ids = set()
        self._build_ui()
        self.refresh_map()

    def _build_ui(self):
        root = QVBoxLayout(self)

        engine_box = QGroupBox("Translate Loaded Rows")
        engine_layout = QHBoxLayout(engine_box)
        engine_layout.addWidget(QLabel("Source:"))
        self.source_lbl = QLabel("<b>(no file loaded)</b>")
        self.source_lbl.setMinimumWidth(150)
        engine_layout.addWidget(self.source_lbl)
        engine_layout.addSpacing(20)
        engine_layout.addWidget(QLabel("Target:"))
        self.target_dialect = QComboBox()
        self.target_dialect.addItems(["ODOT", "VDT"])
        engine_layout.addWidget(self.target_dialect)
        engine_layout.addSpacing(20)
        self.translate_btn = QPushButton("Translate Loaded Rows")
        self.translate_btn.setMinimumWidth(200)
        self.translate_btn.clicked.connect(self._on_translate)
        engine_layout.addWidget(self.translate_btn)
        engine_layout.addStretch(1)
        root.addWidget(engine_box)

        filter_bar = QHBoxLayout()
        filter_bar.addWidget(QLabel("Search:"))
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Code, description, or type:linework ...")
        self.search_box.textChanged.connect(self._apply_filters)
        filter_bar.addWidget(self.search_box, 2)
        filter_bar.addSpacing(15)
        filter_bar.addWidget(QLabel("Show:"))
        self.show_used = QCheckBox("In use")
        self.show_used.setChecked(True)
        self.show_used.toggled.connect(self._apply_filters)
        self.show_exact = QCheckBox("Exact")
        self.show_exact.setChecked(True)
        self.show_exact.toggled.connect(self._apply_filters)
        self.show_best = QCheckBox("Best-guess")
        self.show_best.setChecked(True)
        self.show_best.toggled.connect(self._apply_filters)
        self.show_unmatched = QCheckBox("Unmatched")
        self.show_unmatched.setChecked(True)
        self.show_unmatched.toggled.connect(self._apply_filters)
        self.show_manual = QCheckBox("Manual")
        self.show_manual.setChecked(True)
        self.show_manual.toggled.connect(self._apply_filters)
        for cb in (self.show_used, self.show_exact, self.show_best, self.show_unmatched, self.show_manual):
            filter_bar.addWidget(cb)
        filter_bar.addStretch(1)
        root.addLayout(filter_bar)

        splitter = QSplitter(Qt.Vertical)
        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        splitter.addWidget(self.table)
        self.review_pane = TranslationReviewPane()
        self.review_pane.entry_modified.connect(self._on_entry_modified)
        splitter.addWidget(self.review_pane)
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 1)
        root.addWidget(splitter)

        action_bar = QHBoxLayout()
        self.bulk_accept_btn = QPushButton("Accept all Best-Guess in view")
        self.bulk_accept_btn.clicked.connect(self._on_bulk_accept_best_guess)
        action_bar.addWidget(self.bulk_accept_btn)
        self.save_btn = QPushButton("Save Overrides")
        font = self.save_btn.font()
        font.setBold(True)
        self.save_btn.setFont(font)
        self.save_btn.clicked.connect(self._on_save)
        action_bar.addWidget(self.save_btn)
        action_bar.addStretch(1)
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setFrameShadow(QFrame.Sunken)
        action_bar.addWidget(sep)
        self.export_btn = QPushButton("Export Review CSV")
        self.export_btn.clicked.connect(self._on_export_csv)
        action_bar.addWidget(self.export_btn)
        self.reseed_btn = QPushButton("Reseed from Catalog...")
        self.reseed_btn.setToolTip(
            "Rebuild the translation map from VDT_CODES.xlsx and ODOT_CODES.xlsx.\n"
            "This DISCARDS all manual overrides."
        )
        self.reseed_btn.clicked.connect(self._on_reseed)
        action_bar.addWidget(self.reseed_btn)
        root.addLayout(action_bar)

    def showEvent(self, event):
        self._refresh_source_label()
        self._refresh_used_counts()
        self._populate_table()
        self._refresh_target_default()
        super().showEvent(event)

    def _refresh_source_label(self):
        parent = self._parent_main
        if parent is None or not hasattr(parent, "rows") or not parent.rows:
            self.source_lbl.setText("<b>(no file loaded)</b>")
            return
        cs = getattr(parent, "codeset", None)
        if not cs:
            self.source_lbl.setText("<b>(no codeset)</b>")
            return
        name = str(getattr(cs, "name", "vdt")).upper()
        self.source_lbl.setText(f"<b>{name}</b> (auto-detected)")

    def _refresh_target_default(self):
        parent = self._parent_main
        if parent is None:
            return
        cs = getattr(parent, "codeset", None)
        if not cs:
            return
        src = str(getattr(cs, "name", "vdt")).lower()
        target = "ODOT" if src == "vdt" else "VDT"
        if self.target_dialect.currentText() != target:
            self.target_dialect.blockSignals(True)
            self.target_dialect.setCurrentText(target)
            self.target_dialect.blockSignals(False)

    def _refresh_used_counts(self):
        parent = self._parent_main
        if parent is None or not hasattr(parent, "rows") or not parent.rows:
            self._used_counts = {}
            return
        cs = getattr(parent, "codeset", None)
        dialect = str(getattr(cs, "name", "odot")).lower() if cs else "odot"
        self._used_counts = analyze_used_codes(parent.rows, dialect=dialect)

    def refresh_map(self):
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
        self._refresh_used_counts()
        self._populate_table()

    def _populate_table(self):
        entries = self._map_data.get("entries", [])
        self.table.setRowCount(0)
        used, other = [], []
        for e in entries:
            v = (e.get("vdt") or {}).get("code", "").upper()
            o = (e.get("odot") or {}).get("code", "").upper()
            if v in self._used_counts or o in self._used_counts:
                used.append(e)
            else:
                other.append(e)

        def usage_key(entry):
            v = (entry.get("vdt") or {}).get("code", "").upper()
            o = (entry.get("odot") or {}).get("code", "").upper()
            count = max(self._used_counts.get(v, 0), self._used_counts.get(o, 0))
            return (-count, v or o)

        used.sort(key=usage_key)
        other.sort(key=lambda e: ((e.get("vdt") or {}).get("code", "") or (e.get("odot") or {}).get("code", "")).upper())

        if used:
            self._insert_section_header(f"USED IN LOADED FILE ({len(used)} codes)")
            for e in used:
                self._append_entry_row(e)
        if other:
            self._insert_section_header(f"OTHER CATALOG CODES ({len(other)} codes)")
            for e in other:
                self._append_entry_row(e)
        self._apply_filters()

    def _insert_section_header(self, label):
        row = self.table.rowCount()
        self.table.insertRow(row)
        item = QTableWidgetItem(label)
        font = QFont()
        font.setBold(True)
        item.setFont(font)
        item.setBackground(QBrush(QColor(220, 220, 230)))
        item.setFlags(Qt.ItemIsEnabled)
        self.table.setItem(row, 0, item)
        self.table.setSpan(row, 0, 1, len(COLUMNS))

    def _append_entry_row(self, entry):
        row = self.table.rowCount()
        self.table.insertRow(row)
        vdt = entry.get("vdt") or {}
        odot = entry.get("odot") or {}
        confidence = entry.get("confidence", "unmatched")
        is_dirty = entry.get("id") in self._dirty_entry_ids
        v_code = vdt.get("code", "")
        o_code = odot.get("code", "")
        usage_count = max(
            self._used_counts.get(v_code.upper(), 0),
            self._used_counts.get(o_code.upper(), 0),
        )
        values = [
            "\u25CF" if is_dirty else "",
            "*" if usage_count > 0 else "",
            str(usage_count) if usage_count > 0 else "",
            v_code, vdt.get("type", ""), vdt.get("description", ""),
            o_code, odot.get("type", ""), odot.get("description", ""),
            short_label(entry), describe(entry),
        ]
        color = CONFIDENCE_COLORS.get(confidence)
        for col, val in enumerate(values):
            item = QTableWidgetItem(str(val))
            if color is not None:
                item.setBackground(QBrush(color))
            item.setData(Qt.UserRole, entry.get("id"))
            self.table.setItem(row, col, item)

    def _apply_filters(self):
        search = self.search_box.text().strip().lower()
        type_filter = None
        if search.startswith("type:"):
            type_filter = search[5:].strip()
            search = ""

        for row in range(self.table.rowCount()):
            item0 = self.table.item(row, 0)
            if item0 is None:
                continue
            if self.table.columnSpan(row, 0) > 1:
                continue
            entry_id = item0.data(Qt.UserRole)
            entry = self._find_entry(entry_id)
            if entry is None:
                self.table.setRowHidden(row, True)
                continue
            confidence = entry.get("confidence", "unmatched")
            is_manual = entry.get("user_override", False)
            visible = True
            if is_manual and not self.show_manual.isChecked():
                visible = False
            elif not is_manual:
                if confidence == "exact" and not self.show_exact.isChecked():
                    visible = False
                elif confidence == "best-guess" and not self.show_best.isChecked():
                    visible = False
                elif confidence == "unmatched" and not self.show_unmatched.isChecked():
                    visible = False
            if visible and not self.show_used.isChecked():
                v = (entry.get("vdt") or {}).get("code", "").upper()
                o = (entry.get("odot") or {}).get("code", "").upper()
                if v in self._used_counts or o in self._used_counts:
                    visible = False
            if visible and type_filter:
                vt = (entry.get("vdt") or {}).get("type", "").lower()
                ot = (entry.get("odot") or {}).get("type", "").lower()
                if type_filter not in vt and type_filter not in ot:
                    visible = False
            if visible and search:
                vc = (entry.get("vdt") or {}).get("code", "").lower()
                oc = (entry.get("odot") or {}).get("code", "").lower()
                vd = (entry.get("vdt") or {}).get("description", "").lower()
                od = (entry.get("odot") or {}).get("description", "").lower()
                if search not in vc and search not in oc and search not in vd and search not in od:
                    visible = False
            self.table.setRowHidden(row, not visible)

    def _on_selection_changed(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            self._show_empty_pane_summary()
            return
        item = self.table.item(rows[0].row(), 0)
        if item is None or self.table.columnSpan(rows[0].row(), 0) > 1:
            self._show_empty_pane_summary()
            return
        entry_id = item.data(Qt.UserRole)
        entry = self._find_entry(entry_id)
        if entry is not None:
            self.review_pane.load_entry(entry, self._all_odot_codes(), self._all_vdt_codes())

    def _show_empty_pane_summary(self):
        summary = build_usage_summary(self._used_counts, self._map_data)
        if summary["unique_codes"] == 0:
            html = (
                "<h3>No file loaded</h3>"
                "<p>Open a CSV/TXT file on the Raw Data tab to see usage analysis.</p>"
            )
        else:
            html = (
                f"<h3>Loaded file analysis</h3>"
                f"<p><b>{summary['unique_codes']}</b> unique codes in your data:</p>"
                f"<ul>"
                f"<li>{summary['exact']} exact matches</li>"
                f"<li>{summary['best_guess']} best-guess matches (review recommended)</li>"
                f"<li>{summary['unmatched']} unmatched or missing from catalog</li>"
                f"<li>{summary['manual']} manual overrides</li>"
                f"</ul>"
            )
            if summary["not_in_map"]:
                preview = ", ".join(summary["not_in_map"][:10])
                more = f" ... +{len(summary['not_in_map']) - 10} more" if len(summary["not_in_map"]) > 10 else ""
                html += f"<p><b>Codes not in catalog:</b><br>{preview}{more}</p>"
        self.review_pane.show_summary(html)

    def _find_entry(self, entry_id):
        for e in self._map_data.get("entries", []):
            if e.get("id") == entry_id:
                return e
        return None

    def _all_odot_codes(self):
        codes = set()
        for e in self._map_data.get("entries", []):
            o = e.get("odot")
            if o and o.get("code"):
                codes.add(o["code"])
        return sorted(codes)

    def _all_vdt_codes(self):
        codes = set()
        for e in self._map_data.get("entries", []):
            v = e.get("vdt")
            if v and v.get("code"):
                codes.add(v["code"])
        return sorted(codes)

    def _on_entry_modified(self, entry_id):
        if entry_id:
            self._dirty_entry_ids.add(entry_id)
        self._populate_table()
        self.map_modified.emit()

    def _on_translate(self):
        from app.services.description_translator import translate_rows
        parent = self._parent_main
        if parent is None or not hasattr(parent, "rows") or not parent.rows:
            QMessageBox.information(self, "Translate",
                "No rows loaded. Open a CSV/TXT file on the Raw Data tab first.")
            return
        cs = getattr(parent, "codeset", None)
        src = str(getattr(cs, "name", "vdt")).upper() if cs else "VDT"
        tgt = self.target_dialect.currentText()
        if src == tgt:
            QMessageBox.warning(self, "Same Source and Target",
                f"Source and target are both {src}. Nothing to translate.")
            return
        direction = "vdt_to_odot" if src == "VDT" else "odot_to_vdt"
        resp = QMessageBox.question(
            self, "Translate Loaded Rows",
            f"Translate {len(parent.rows)} rows from {src} to {tgt}?\n\n"
            "This rewrites the Description (D) column in place.\n"
            "Point numbers, N, E, and Z are NEVER modified.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if resp != QMessageBox.Yes:
            return
        try:
            _, summary = translate_rows(parent.rows, direction, map_data=self._map_data)
        except Exception as e:
            QMessageBox.critical(self, "Translation Failed", str(e))
            return
        if hasattr(parent, "results") and hasattr(parent, "codeset"):
            try:
                from app.services.validator import validate_rows as _validate
                from app.services.suggester import build_suggestions as _suggest
                parent.results = _validate(parent.rows, parent.codeset)
                parent.suggestions = _suggest(parent.rows, parent.codeset, parent.results)
            except Exception:
                pass
        if hasattr(parent, "_populate_table"):
            parent._populate_table()
        if hasattr(parent, "modified_tab"):
            parent.modified_tab.refresh_from_parent()
        QMessageBox.information(self, "Translation Complete",
            f"Translation {src} -> {tgt} applied.\n\n"
            f"Rows changed: {summary['rows_changed']}\n"
            f"Code changes: {summary['code_changes']}\n"
            f"Linework changes: {summary['linework_changes']}")

    def _on_bulk_accept_best_guess(self):
        targets = []
        for row in range(self.table.rowCount()):
            if self.table.isRowHidden(row):
                continue
            if self.table.columnSpan(row, 0) > 1:
                continue
            item = self.table.item(row, 0)
            if item is None:
                continue
            entry_id = item.data(Qt.UserRole)
            entry = self._find_entry(entry_id)
            if entry and entry.get("confidence") == "best-guess" and not entry.get("user_override"):
                targets.append(entry)
        if not targets:
            QMessageBox.information(self, "Nothing to Accept",
                "No best-guess entries are currently visible.")
            return
        resp = QMessageBox.question(self, "Accept All Best-Guess",
            f"Mark all {len(targets)} visible best-guess entries as manual overrides?\n\n"
            "You can still edit individual entries afterward.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if resp != QMessageBox.Yes:
            return
        for entry in targets:
            entry["user_override"] = True
            entry["confidence"] = "manual"
            self._dirty_entry_ids.add(entry.get("id"))
        self._populate_table()
        self.map_modified.emit()

    def _on_reseed(self):
        resp = QMessageBox.question(self, "Reseed from Catalog",
            "<b>This will rebuild the translation map from VDT_CODES.xlsx + ODOT_CODES.xlsx.</b><br><br>"
            "All manual overrides will be <b>permanently discarded</b>.<br><br>Continue?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if resp != QMessageBox.Yes:
            return
        from app.services import seed_translation_map as seeder
        try:
            seeder.seed(force=True)
        except Exception as e:
            QMessageBox.critical(self, "Reseed Failed", str(e))
            return
        self._dirty_entry_ids.clear()
        self.refresh_map()
        QMessageBox.information(self, "Reseed Complete", "Translation map regenerated.")

    def _on_export_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Review CSV", "translation_map_review.csv", "CSV (*.csv)")
        if not path:
            return
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(COLUMNS)
            for row in range(self.table.rowCount()):
                if self.table.isRowHidden(row):
                    continue
                if self.table.columnSpan(row, 0) > 1:
                    continue
                writer.writerow([
                    (self.table.item(row, c).text() if self.table.item(row, c) else "")
                    for c in range(len(COLUMNS))
                ])
        QMessageBox.information(self, "Export Complete", f"Wrote {path}")

    def _on_save(self):
        try:
            tm.save(self._map_data)
        except Exception as e:
            QMessageBox.critical(self, "Save Failed", str(e))
            return
        self._dirty_entry_ids.clear()
        self._populate_table()
        QMessageBox.information(self, "Saved", "Overrides written to translation_map.json")
