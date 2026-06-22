"""Wide bottom-mounted review pane for the Translation Tab (v0.5.1)."""
from __future__ import annotations
from typing import Optional, Dict

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QComboBox,
    QLineEdit, QTextEdit, QPushButton, QGroupBox, QStackedWidget,
)

from app.services.match_basis_descriptor import describe


class TranslationReviewPane(QWidget):
    entry_modified = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._entry: Optional[Dict] = None
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        self.stack = QStackedWidget()
        root.addWidget(self.stack)
        self._build_edit_page()
        self._build_summary_page()
        self.stack.setCurrentIndex(1)

    def _build_edit_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        editors = QHBoxLayout()

        vdt_box = QGroupBox("VDT")
        vdt_grid = QGridLayout(vdt_box)
        self.vdt_code_edit = QLineEdit()
        self.vdt_type_edit = QLineEdit()
        self.vdt_desc_edit = QLineEdit()
        vdt_grid.addWidget(QLabel("Code:"), 0, 0)
        vdt_grid.addWidget(self.vdt_code_edit, 0, 1)
        vdt_grid.addWidget(QLabel("Type:"), 1, 0)
        vdt_grid.addWidget(self.vdt_type_edit, 1, 1)
        vdt_grid.addWidget(QLabel("Desc:"), 2, 0)
        vdt_grid.addWidget(self.vdt_desc_edit, 2, 1)
        editors.addWidget(vdt_box)

        odot_box = QGroupBox("ODOT")
        odot_grid = QGridLayout(odot_box)
        self.odot_code_combo = QComboBox()
        self.odot_code_combo.setEditable(True)
        self.odot_type_edit = QLineEdit()
        self.odot_desc_edit = QLineEdit()
        odot_grid.addWidget(QLabel("Code:"), 0, 0)
        odot_grid.addWidget(self.odot_code_combo, 0, 1)
        odot_grid.addWidget(QLabel("Type:"), 1, 0)
        odot_grid.addWidget(self.odot_type_edit, 1, 1)
        odot_grid.addWidget(QLabel("Desc:"), 2, 0)
        odot_grid.addWidget(self.odot_desc_edit, 2, 1)
        editors.addWidget(odot_box)

        layout.addLayout(editors)

        self.match_basis_lbl = QLabel("<i>No entry selected.</i>")
        self.match_basis_lbl.setWordWrap(True)
        self.match_basis_lbl.setStyleSheet("padding: 4px; background-color: #f0f0f0;")
        layout.addWidget(self.match_basis_lbl)

        layout.addWidget(QLabel("Notes:"))
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)
        layout.addWidget(self.notes_edit)

        btn_row = QHBoxLayout()
        self.save_btn = QPushButton("Save Changes")
        self.save_btn.clicked.connect(self._on_save)
        self.revert_btn = QPushButton("Revert")
        self.revert_btn.clicked.connect(self._on_revert)
        btn_row.addWidget(self.save_btn)
        btn_row.addWidget(self.revert_btn)
        btn_row.addStretch(1)
        layout.addLayout(btn_row)

        self.stack.addWidget(page)

    def _build_summary_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        self.summary_label = QLabel("<h3>No file loaded</h3>")
        self.summary_label.setWordWrap(True)
        self.summary_label.setTextFormat(Qt.RichText)
        self.summary_label.setAlignment(Qt.AlignTop)
        layout.addWidget(self.summary_label)
        layout.addStretch(1)
        self.stack.addWidget(page)

    def load_entry(self, entry, all_odot_codes, all_vdt_codes):
        self._entry = entry
        vdt = entry.get("vdt") or {}
        odot = entry.get("odot") or {}
        self.vdt_code_edit.setText(vdt.get("code", ""))
        self.vdt_type_edit.setText(vdt.get("type", ""))
        self.vdt_desc_edit.setText(vdt.get("description", ""))
        self.odot_code_combo.blockSignals(True)
        self.odot_code_combo.clear()
        self.odot_code_combo.addItems([""] + all_odot_codes)
        self.odot_code_combo.setCurrentText(odot.get("code", ""))
        self.odot_code_combo.blockSignals(False)
        self.odot_type_edit.setText(odot.get("type", ""))
        self.odot_desc_edit.setText(odot.get("description", ""))
        self.notes_edit.setPlainText(entry.get("notes", ""))
        self.match_basis_lbl.setText(f"<b>Why this match?</b> {describe(entry)}")
        self.stack.setCurrentIndex(0)

    def show_summary(self, html):
        self.summary_label.setText(html)
        self.stack.setCurrentIndex(1)

    def clear_entry(self):
        self._entry = None
        self.show_summary("<h3>No file loaded</h3>")

    def _on_save(self):
        if not self._entry:
            return
        v_code = self.vdt_code_edit.text().strip()
        v_type = self.vdt_type_edit.text().strip()
        v_desc = self.vdt_desc_edit.text().strip()
        o_code = self.odot_code_combo.currentText().strip()
        o_type = self.odot_type_edit.text().strip()
        o_desc = self.odot_desc_edit.text().strip()
        if v_code or v_type or v_desc:
            if self._entry.get("vdt") is None:
                self._entry["vdt"] = {}
            self._entry["vdt"]["code"] = v_code
            self._entry["vdt"]["type"] = v_type
            self._entry["vdt"]["description"] = v_desc
        if o_code or o_type or o_desc:
            if self._entry.get("odot") is None:
                self._entry["odot"] = {}
            self._entry["odot"]["code"] = o_code
            self._entry["odot"]["type"] = o_type
            self._entry["odot"]["description"] = o_desc
        self._entry["notes"] = self.notes_edit.toPlainText()
        self._entry["user_override"] = True
        self._entry["confidence"] = "manual"
        self.entry_modified.emit(self._entry.get("id", ""))

    def _on_revert(self):
        if not self._entry:
            return
        self._entry["user_override"] = False
        self._entry["notes"] = ""
        self.entry_modified.emit(self._entry.get("id", ""))
