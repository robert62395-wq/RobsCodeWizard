# v0.5.5 translation style fix
"""Translation Tab v0.5.1.2 - simplified Raw-Data-style layout.
v0.5.2.3 help icons translation_tab applied.
v0.5.2.3 tooltips translation_tab applied."""
from __future__ import annotations
import csv
import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QBrush
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QComboBox, QLineEdit, QPushButton, QLabel, QMessageBox, QFileDialog,
    QHeaderView, QCheckBox, QDialog, QGridLayout, QTextEdit, QFrame,
)

from app.services import translation_map as tm
from app.services.usage_analyzer import analyze_used_codes
from app.services.match_basis_descriptor import short_label
from app.services.settings import load_settings, set_setting
from app.ui.help_icon import HelpIcon

log = logging.getLogger("robs_code_wizard")

CONFIDENCE_COLORS = {
    "exact": QColor(200, 240, 200),
    "best-guess": QColor(255, 245, 180),
    "unmatched": QColor(255, 200, 200),
    "manual": QColor(200, 220, 255),
}

COLUMNS = ["VDT Code", "VDT Description", "ODOT Code", "ODOT Description",
           "Confidence", "Count", "Notes"]


class EntryEditDialog(QDialog):
    def __init__(self, entry, all_odot_codes, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Translation Entry")
        self.resize(600, 350)
        self._entry = entry
        self._build_ui(all_odot_codes)

    def _build_ui(self, all_odot_codes):
        layout = QGridLayout(self)
        vdt = self._entry.get("vdt") or {}
        odot = self._entry.get("odot") or {}
        layout.addWidget(QLabel("<b>VDT side</b>"), 0, 0, 1, 2)
        layout.addWidget(QLabel("Code:"), 1, 0)
        self.vdt_code = QLineEdit(vdt.get("code", ""))
        layout.addWidget(self.vdt_code, 1, 1)
        layout.addWidget(QLabel("Description:"), 2, 0)
        self.vdt_desc = QLineEdit(vdt.get("description", ""))
        layout.addWidget(self.vdt_desc, 2, 1)
        layout.addWidget(QLabel("<b>ODOT side</b>"), 3, 0, 1, 2)
        layout.addWidget(QLabel("Code:"), 4, 0)
        self.odot_code = QComboBox()
        self.odot_code.setEditable(True)
        self.odot_code.addItems([""] + all_odot_codes)
        self.odot_code.setCurrentText(odot.get("code", ""))
        layout.addWidget(self.odot_code, 4, 1)
        layout.addWidget(QLabel("Description:"), 5, 0)
        self.odot_desc = QLineEdit(odot.get("description", ""))
        layout.addWidget(self.odot_desc, 5, 1)
        layout.addWidget(QLabel("Notes:"), 6, 0)
        self.notes = QTextEdit()
        self.notes.setPlainText(self._entry.get("notes", ""))
        self.notes.setMaximumHeight(70)
        layout.addWidget(self.notes, 6, 1)
        btns = QHBoxLayout()
        save = QPushButton("Save")
        save.clicked.connect(self.accept)
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        btns.addStretch(1)
        btns.addWidget(save)
        btns.addWidget(cancel)
        layout.addLayout(btns, 7, 0, 1, 2)

    def apply_changes(self):
        if self._entry.get("vdt") is None:
            self._entry["vdt"] = {}
        self._entry["vdt"]["code"] = self.vdt_code.text().strip()
        self._entry["vdt"]["description"] = self.vdt_desc.text().strip()
        if self._entry.get("odot") is None:
            self._entry["odot"] = {}
        self._entry["odot"]["code"] = self.odot_code.currentText().strip()
        self._entry["odot"]["description"] = self.odot_desc.text().strip()
        self._entry["notes"] = self.notes.toPlainText()
        self._entry["user_override"] = True
        self._entry["confidence"] = "manual"


class TranslationTab(QWidget):
    map_modified = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._parent_main = parent
        self._map_data = {"entries": []}
        self._used_counts = {}
        self._dirty_ids = set()
        self._build_ui()
        self._safe_refresh()

    def _build_under_construction_banner(self):
        """v0.5.2.3 — warns users this tab is being rebuilt."""
        settings = load_settings()
        if settings.get("translation_under_construction_hidden", False):
            return None

        frame = QFrame()
        frame.setStyleSheet(
            "QFrame { background-color: #FFF3CD; border: 2px solid #FFB300;"
            " border-radius: 4px; padding: 8px; }"
        )
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(10, 6, 10, 6)

        icon_lbl = QLabel("[!]")
        icon_lbl.setStyleSheet("font-size: 18px; font-weight: bold; background: transparent; border: none; color: #d35400;")
        layout.addWidget(icon_lbl)

        msg_lbl = QLabel(
            "<b>Under construction.</b> The Translation tab is being rebuilt. "
            "The automatic matching algorithm produces low-quality suggestions today. "
            "Manual review of every entry is recommended before saving overrides."
        )
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(msg_lbl, 1)

        dismiss_btn = QPushButton("Dismiss for this session")
        dismiss_btn.setStyleSheet("padding: 4px 10px;")
        dismiss_btn.clicked.connect(lambda: frame.setVisible(False))
        layout.addWidget(dismiss_btn)

        hide_forever_btn = QPushButton("Don't show again")
        hide_forever_btn.setStyleSheet("padding: 4px 10px;")
        def _hide_forever():
            set_setting("translation_under_construction_hidden", True)
            frame.setVisible(False)
        hide_forever_btn.clicked.connect(_hide_forever)
        layout.addWidget(hide_forever_btn)

        return frame

    def _build_ui(self):
        root = QVBoxLayout(self)
        # v0.5.2.3 under construction banner
        _uc = self._build_under_construction_banner()
        if _uc is not None:
            root.addWidget(_uc)
        self.status_lbl = QLabel("Loading...")
        self.status_lbl.setWordWrap(True)
        root.addWidget(self.status_lbl)

        # Top toolbar - mimics Raw Data tab style
        bar = QHBoxLayout()
        bar.addWidget(QLabel("Source:"))
        self.source_lbl = QLabel("<b>(none)</b>")
        bar.addWidget(self.source_lbl)
        bar.addSpacing(20)
        bar.addWidget(QLabel("Target:"))
        self.target_combo = QComboBox()
        self.target_combo.addItems(["ODOT", "VDT"])
        self.target_combo.setToolTip("Dialect to translate loaded rows into (defaults to opposite of Source)")
        bar.addWidget(self.target_combo)
        bar.addWidget(HelpIcon("translate_source_target"))
        bar.addSpacing(20)
        self.translate_btn = QPushButton("Translate Loaded Rows")
        self.translate_btn.setToolTip("Rewrite the Description column on all loaded rows. P, N, E, Z never modified.")
        self.translate_btn.clicked.connect(self._on_translate)
        bar.addWidget(self.translate_btn)
        bar.addWidget(HelpIcon("translate_button"))
        bar.addStretch(1)
        bar.addWidget(QLabel("Search:"))
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("code or description...")
        self.search_box.setToolTip("Filter rows by VDT/ODOT code or description text")
        self.search_box.setMaximumWidth(250)
        self.search_box.textChanged.connect(self._apply_filter)
        bar.addWidget(self.search_box)
        root.addLayout(bar)

        # Filter row
        filt = QHBoxLayout()
        filt.addWidget(QLabel("Show:"))
        self.show_used_only = QCheckBox("Only codes in loaded file")
        self.show_used_only.setToolTip("Show only entries for codes that appear in your loaded file")
        self.show_used_only.setChecked(True)
        self.show_used_only.toggled.connect(self._apply_filter)
        self.show_unmatched = QCheckBox("Unmatched")
        self.show_unmatched.setToolTip("Show entries with no automatic match")
        self.show_unmatched.setChecked(True)
        self.show_unmatched.toggled.connect(self._apply_filter)
        self.show_bestguess = QCheckBox("Best-guess")
        self.show_bestguess.setToolTip("Show entries matched by description similarity")
        self.show_bestguess.setChecked(True)
        self.show_bestguess.toggled.connect(self._apply_filter)
        self.show_exact = QCheckBox("Exact")
        self.show_exact.setToolTip("Show entries with exact code-equality matches")
        self.show_exact.setChecked(True)
        self.show_exact.toggled.connect(self._apply_filter)
        self.show_manual = QCheckBox("Manual")
        self.show_manual.setToolTip("Show entries you have manually overridden")
        self.show_manual.setChecked(True)
        self.show_manual.toggled.connect(self._apply_filter)
        for cb in (self.show_used_only, self.show_unmatched, self.show_bestguess,
                   self.show_exact, self.show_manual):
            filt.addWidget(cb)
        filt.addStretch(1)
        filt.insertWidget(filt.count() - 1, HelpIcon("translate_filter_used"))
        root.addLayout(filt)

        # Main table (7 columns, no section headers, no review pane)
        self.table = QTableWidget(0, len(COLUMNS))
        # v0.5.5 translation style fix
        try:
            self.table.setStyleSheet("""
            QTableView, QTableWidget {
                color: #000000;
                background-color: #FFFFFF;
                gridline-color: #CCCCCC;
            }
            QHeaderView::section {
                background-color: #E6E6E6;
                color: #000000;
                font-weight: bold;
            }
            """)
        except Exception:
            pass
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.cellDoubleClicked.connect(self._on_double_click)
        root.addWidget(self.table)

        # Bottom action bar
        action = QHBoxLayout()
        self.bulk_btn = QPushButton("Accept all Best-Guess in view")
        self.bulk_btn.setToolTip("Promote every visible best-guess to a manual override in one click")
        self.bulk_btn.clicked.connect(self._on_bulk_accept)
        action.addWidget(self.bulk_btn)
        action.addWidget(HelpIcon("translate_bulk_accept"))
        self.save_btn = QPushButton("Save Overrides")
        self.save_btn.setToolTip("Persist all manual overrides to translation_map.json")
        font = self.save_btn.font()
        font.setBold(True)
        self.save_btn.setFont(font)
        self.save_btn.clicked.connect(self._on_save)
        action.addWidget(self.save_btn)
        action.addStretch(1)
        self.export_btn = QPushButton("Export Review CSV")
        self.export_btn.setToolTip("Export the visible rows to CSV for offline review")
        self.export_btn.clicked.connect(self._on_export)
        action.addWidget(self.export_btn)
        self.reseed_btn = QPushButton("Reseed from Catalog...")
        self.reseed_btn.setToolTip("DESTRUCTIVE: Rebuild map from VDT_CODES.xlsx and ODOT_CODES.xlsx. Discards all manual overrides.")
        self.reseed_btn.clicked.connect(self._on_reseed)
        action.addWidget(self.reseed_btn)
        action.addWidget(HelpIcon("translate_reseed"))
        root.addLayout(action)

    def showEvent(self, event):
        self._safe_refresh()
        super().showEvent(event)

    def _safe_refresh(self):
        try:
            self._refresh_source()
            self._refresh_used()
            self._refresh_map()
            self._populate()
            self._refresh_target()
            self._update_status()
        except Exception as e:
            log.exception("translation tab refresh failed: %s", e)
            self.status_lbl.setText(f"<b style='color:red;'>Error: {e}</b>")

    def _refresh_source(self):
        parent = self._parent_main
        if parent is None or not getattr(parent, "rows", None):
            self.source_lbl.setText("<b>(no file loaded)</b>")
            return
        cs = getattr(parent, "codeset", None)
        name = str(getattr(cs, "name", "vdt")).upper() if cs else "VDT"
        self.source_lbl.setText(f"<b>{name}</b>")

    def _refresh_target(self):
        parent = self._parent_main
        if parent is None:
            return
        cs = getattr(parent, "codeset", None)
        if not cs:
            return
        src = str(getattr(cs, "name", "vdt")).lower()
        target = "ODOT" if src == "vdt" else "VDT"
        if self.target_combo.currentText() != target:
            self.target_combo.blockSignals(True)
            self.target_combo.setCurrentText(target)
            self.target_combo.blockSignals(False)

    def _refresh_used(self):
        parent = self._parent_main
        if parent is None or not getattr(parent, "rows", None):
            self._used_counts = {}
            return
        cs = getattr(parent, "codeset", None)
        dialect = str(getattr(cs, "name", "odot")).lower() if cs else "odot"
        self._used_counts = analyze_used_codes(parent.rows, dialect=dialect)

    def _refresh_map(self):
        try:
            self._map_data = tm.load()
        except Exception as e:
            log.exception("map load failed: %s", e)
            self._map_data = {"entries": []}

    def _update_status(self):
        n_entries = len(self._map_data.get("entries", []))
        parent = self._parent_main
        rows = len(parent.rows) if (parent and getattr(parent, "rows", None)) else 0
        used = len(self._used_counts)
        if n_entries == 0:
            self.status_lbl.setText(
                "<b style='color:#cc4400;'>Translation map is empty.</b> "
                "Click <b>Reseed from Catalog...</b> below."
            )
        elif rows == 0:
            self.status_lbl.setText(
                f"<b>Map:</b> {n_entries} entries. <b>No file loaded.</b>"
            )
        else:
            self.status_lbl.setText(
                f"<b>Map:</b> {n_entries} entries &nbsp;|&nbsp; "
                f"<b>File:</b> {rows} rows &nbsp;|&nbsp; "
                f"<b>Unique codes in file:</b> {used}"
            )

    def _populate(self):
        entries = self._map_data.get("entries", [])
        self.table.setRowCount(0)
        for entry in sorted(entries, key=lambda e: (
            (e.get("vdt") or {}).get("code", "") or (e.get("odot") or {}).get("code", "")
        )):
            self._append_row(entry)
        self._apply_filter()

    def _append_row(self, entry):
        row = self.table.rowCount()
        self.table.insertRow(row)
        vdt = entry.get("vdt") or {}
        odot = entry.get("odot") or {}
        conf = entry.get("confidence", "unmatched")
        v_code = vdt.get("code", "")
        o_code = odot.get("code", "")
        count = max(
            self._used_counts.get(v_code.upper(), 0),
            self._used_counts.get(o_code.upper(), 0),
        )
        values = [
            v_code, vdt.get("description", ""),
            o_code, odot.get("description", ""),
            short_label(entry), str(count) if count else "",
            entry.get("notes", ""),
        ]
        color = CONFIDENCE_COLORS.get(conf)
        for col, val in enumerate(values):
            item = QTableWidgetItem(str(val))
            if color:
                item.setBackground(QBrush(color))
            item.setData(Qt.UserRole, entry.get("id"))
            self.table.setItem(row, col, item)

    def _apply_filter(self):
        search = self.search_box.text().strip().lower()
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item is None:
                continue
            entry_id = item.data(Qt.UserRole)
            entry = self._find_entry(entry_id)
            if entry is None:
                continue
            visible = True
            conf = entry.get("confidence", "unmatched")
            is_manual = entry.get("user_override", False)
            if is_manual and not self.show_manual.isChecked():
                visible = False
            elif not is_manual:
                if conf == "exact" and not self.show_exact.isChecked():
                    visible = False
                elif conf == "best-guess" and not self.show_bestguess.isChecked():
                    visible = False
                elif conf == "unmatched" and not self.show_unmatched.isChecked():
                    visible = False
            if visible and self.show_used_only.isChecked():
                v = (entry.get("vdt") or {}).get("code", "").upper()
                o = (entry.get("odot") or {}).get("code", "").upper()
                if v not in self._used_counts and o not in self._used_counts:
                    visible = False
            if visible and search:
                vc = (entry.get("vdt") or {}).get("code", "").lower()
                oc = (entry.get("odot") or {}).get("code", "").lower()
                vd = (entry.get("vdt") or {}).get("description", "").lower()
                od = (entry.get("odot") or {}).get("description", "").lower()
                if not any(search in x for x in (vc, oc, vd, od)):
                    visible = False
            self.table.setRowHidden(row, not visible)

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

    def _on_double_click(self, row, col):
        item = self.table.item(row, 0)
        if item is None:
            return
        entry_id = item.data(Qt.UserRole)
        entry = self._find_entry(entry_id)
        if entry is None:
            return
        dlg = EntryEditDialog(entry, self._all_odot_codes(), self)
        if dlg.exec():
            dlg.apply_changes()
            self._dirty_ids.add(entry.get("id"))
            self._populate()
            self.map_modified.emit()

    def _on_translate(self):
        from app.services.description_translator import translate_rows
        parent = self._parent_main
        if parent is None or not getattr(parent, "rows", None):
            QMessageBox.information(self, "Translate",
                "No rows loaded. Open a CSV/TXT file on the Raw Data tab first.")
            return
        cs = getattr(parent, "codeset", None)
        src = str(getattr(cs, "name", "vdt")).upper() if cs else "VDT"
        tgt = self.target_combo.currentText()
        if src == tgt:
            QMessageBox.warning(self, "Same Source",
                f"Source and target are both {src}.")
            return
        direction = "vdt_to_odot" if src == "VDT" else "odot_to_vdt"
        resp = QMessageBox.question(self, "Translate",
            f"Translate {len(parent.rows)} rows from {src} to {tgt}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if resp != QMessageBox.Yes:
            return
        try:
            _, summary = translate_rows(parent.rows, direction, map_data=self._map_data)
        except Exception as e:
            QMessageBox.critical(self, "Translation Failed", str(e))
            return
        if hasattr(parent, "_populate_table"):
            try:
                from app.services.validator import validate_rows as _v
                from app.services.suggester import build_suggestions as _s
                parent.results = _v(parent.rows, parent.codeset)
                parent.suggestions = _s(parent.rows, parent.codeset, parent.results)
                parent._populate_table()
                if hasattr(parent, "modified_tab"):
                    parent.modified_tab.refresh_from_parent()
            except Exception:
                pass
        QMessageBox.information(self, "Translation Complete",
            f"{src} -> {tgt}: {summary['rows_changed']} rows changed, "
            f"{summary['code_changes']} code changes, "
            f"{summary['linework_changes']} linework changes.")

    def _on_bulk_accept(self):
        targets = []
        for row in range(self.table.rowCount()):
            if self.table.isRowHidden(row):
                continue
            item = self.table.item(row, 0)
            if item is None:
                continue
            entry = self._find_entry(item.data(Qt.UserRole))
            if entry and entry.get("confidence") == "best-guess" and not entry.get("user_override"):
                targets.append(entry)
        if not targets:
            QMessageBox.information(self, "Nothing to Accept",
                "No best-guess entries visible.")
            return
        resp = QMessageBox.question(self, "Accept All",
            f"Mark all {len(targets)} visible best-guess entries as manual overrides?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if resp != QMessageBox.Yes:
            return
        for entry in targets:
            entry["user_override"] = True
            entry["confidence"] = "manual"
            self._dirty_ids.add(entry.get("id"))
        self._populate()
        self.map_modified.emit()

    def _on_save(self):
        try:
            tm.save(self._map_data)
        except Exception as e:
            QMessageBox.critical(self, "Save Failed", str(e))
            return
        self._dirty_ids.clear()
        QMessageBox.information(self, "Saved",
            "Overrides written to translation_map.json")

    def _on_export(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export CSV",
            "translation_review.csv", "CSV (*.csv)")
        if not path:
            return
        with open(path, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(COLUMNS)
            for row in range(self.table.rowCount()):
                if self.table.isRowHidden(row):
                    continue
                w.writerow([
                    (self.table.item(row, c).text() if self.table.item(row, c) else "")
                    for c in range(len(COLUMNS))
                ])
        QMessageBox.information(self, "Exported", f"Wrote {path}")

    def _on_reseed(self):
        resp = QMessageBox.question(self, "Reseed from Catalog",
            "Rebuild the translation map from VDT_CODES.xlsx + ODOT_CODES.xlsx. "
            "All manual overrides will be permanently discarded. Continue?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if resp != QMessageBox.Yes:
            return
        from app.services import seed_translation_map as seeder
        try:
            seeder.seed(force=True)
        except Exception as e:
            QMessageBox.critical(self, "Reseed Failed", str(e))
            return
        self._dirty_ids.clear()
        self._safe_refresh()
        QMessageBox.information(self, "Done", "Translation map regenerated.")