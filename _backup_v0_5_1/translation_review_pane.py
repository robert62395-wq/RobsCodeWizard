"""Right-side review pane for editing a single translation map entry."""
from __future__ import annotations

from typing import Dict, List, Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel, QComboBox,
    QTextEdit, QPushButton, QHBoxLayout, QGroupBox,
)


class TranslationReviewPane(QWidget):
    """Edit override + notes for a single translation map entry."""

    entry_modified = Signal(str)  # emits entry_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self._entry: Optional[Dict] = None
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)

        # VDT details
        vdt_box = QGroupBox("VDT")
        vdt_form = QFormLayout(vdt_box)
        self.vdt_code_lbl = QLabel("-")
        self.vdt_type_lbl = QLabel("-")
        self.vdt_desc_lbl = QLabel("-")
        self.vdt_desc_lbl.setWordWrap(True)
        vdt_form.addRow("Code:", self.vdt_code_lbl)
        vdt_form.addRow("Type:", self.vdt_type_lbl)
        vdt_form.addRow("Desc:", self.vdt_desc_lbl)
        root.addWidget(vdt_box)

        # ODOT override
        odot_box = QGroupBox("ODOT (override)")
        odot_form = QFormLayout(odot_box)
        self.odot_code_combo = QComboBox()
        self.odot_code_combo.setEditable(True)
        self.confidence_lbl = QLabel("-")
        odot_form.addRow("ODOT Code:", self.odot_code_combo)
        odot_form.addRow("Confidence:", self.confidence_lbl)
        root.addWidget(odot_box)

        # Notes
        root.addWidget(QLabel("Notes:"))
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(120)
        root.addWidget(self.notes_edit)

        # Action buttons
        btn_row = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self._on_save)
        self.revert_btn = QPushButton("Revert")
        self.revert_btn.clicked.connect(self._on_revert)
        btn_row.addWidget(self.save_btn)
        btn_row.addWidget(self.revert_btn)
        btn_row.addStretch(1)
        root.addLayout(btn_row)
        root.addStretch(1)

        self.setEnabled(False)

    def load_entry(self, entry: Dict, all_odot_codes: List[str]) -> None:
        self._entry = entry
        self.setEnabled(True)

        vdt = entry.get("vdt") or {}
        self.vdt_code_lbl.setText(vdt.get("code", "-"))
        self.vdt_type_lbl.setText(vdt.get("type", "-"))
        self.vdt_desc_lbl.setText(vdt.get("description", "-"))

        odot = entry.get("odot") or {}
        self.odot_code_combo.blockSignals(True)
        self.odot_code_combo.clear()
        self.odot_code_combo.addItems([""] + all_odot_codes)
        self.odot_code_combo.setCurrentText(odot.get("code", ""))
        self.odot_code_combo.blockSignals(False)

        self.confidence_lbl.setText(entry.get("confidence", "-"))
        self.notes_edit.setPlainText(entry.get("notes", ""))

    def clear_entry(self) -> None:
        self._entry = None
        self.setEnabled(False)
        self.vdt_code_lbl.setText("-")
        self.vdt_type_lbl.setText("-")
        self.vdt_desc_lbl.setText("-")
        self.confidence_lbl.setText("-")
        self.notes_edit.clear()

    def _on_save(self) -> None:
        if not self._entry:
            return
        new_code = self.odot_code_combo.currentText().strip()
        if new_code:
            if self._entry.get("odot") is None:
                self._entry["odot"] = {"code": new_code, "type": "", "description": ""}
            else:
                self._entry["odot"]["code"] = new_code
        self._entry["notes"] = self.notes_edit.toPlainText()
        self._entry["user_override"] = True
        self._entry["confidence"] = "manual"
        self.entry_modified.emit(self._entry.get("id", ""))

    def _on_revert(self) -> None:
        if not self._entry:
            return
        self._entry["user_override"] = False
        self._entry["notes"] = ""
        # Confidence + odot fields are restored on next reseed; leave intact for now.
        self.entry_modified.emit(self._entry.get("id", ""))
