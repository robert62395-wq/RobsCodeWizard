"""Tools > Convert Line Connect Codes dialog (v0.4.5: reverse direction enabled)."""
from __future__ import annotations
from typing import List, Dict

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QRadioButton,
    QPushButton, QTableWidget, QTableWidgetItem, QLabel, QHeaderView,
)

from app.services.line_connect_translator import (
    convert_numeric_to_alpha, convert_alpha_to_numeric, preview_changes,
)


class ConvertLineConnectDialog(QDialog):
    def __init__(self, rows, selected_rows=None, parent=None):
        super().__init__(parent)
        self._all_rows = rows
        self._selected_rows = selected_rows or []
        self.setWindowTitle("Convert Line Connect Codes")
        self.resize(720, 480)
        self._build_ui()
        self._refresh_preview()

    def _build_ui(self):
        root = QVBoxLayout(self)
        dir_box = QGroupBox("Direction")
        dir_layout = QHBoxLayout(dir_box)
        self.dir_num_to_alpha = QRadioButton("Numeric -> Alphabetic (Civil3D)")
        self.dir_num_to_alpha.setChecked(True)
        self.dir_num_to_alpha.toggled.connect(self._refresh_preview)
        self.dir_alpha_to_num = QRadioButton("Alphabetic -> Numeric (OpenRoads)")
        self.dir_alpha_to_num.toggled.connect(self._refresh_preview)
        dir_layout.addWidget(self.dir_num_to_alpha)
        dir_layout.addWidget(self.dir_alpha_to_num)
        root.addWidget(dir_box)

        scope_box = QGroupBox("Scope")
        scope_layout = QHBoxLayout(scope_box)
        self.scope_all = QRadioButton("All rows")
        self.scope_all.setChecked(True)
        self.scope_sel = QRadioButton("Selection only")
        self.scope_sel.setEnabled(bool(self._selected_rows))
        if not self._selected_rows:
            self.scope_sel.setToolTip("No rows selected in the active tab.")
        self.scope_all.toggled.connect(self._refresh_preview)
        self.scope_sel.toggled.connect(self._refresh_preview)
        scope_layout.addWidget(self.scope_all)
        scope_layout.addWidget(self.scope_sel)
        root.addWidget(scope_box)

        root.addWidget(QLabel("Preview (first 20 changed rows):"))
        self.preview_table = QTableWidget(0, 3)
        self.preview_table.setHorizontalHeaderLabels(["Point #", "Before", "After"])
        self.preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.preview_table.setEditTriggers(QTableWidget.NoEditTriggers)
        root.addWidget(self.preview_table)

        self.summary_lbl = QLabel("0 rows will change.")
        root.addWidget(self.summary_lbl)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        self.refresh_btn = QPushButton("Refresh Preview")
        self.refresh_btn.clicked.connect(self._refresh_preview)
        self.apply_btn = QPushButton("Apply")
        self.apply_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(self.refresh_btn)
        btn_row.addWidget(self.apply_btn)
        btn_row.addWidget(self.cancel_btn)
        root.addLayout(btn_row)

    def _current_rows(self):
        return self._selected_rows if self.scope_sel.isChecked() else self._all_rows

    def _direction(self):
        return "numeric_to_alpha" if self.dir_num_to_alpha.isChecked() else "alpha_to_numeric"

    def _convert_fn(self):
        return convert_numeric_to_alpha if self.dir_num_to_alpha.isChecked() else convert_alpha_to_numeric

    def _refresh_preview(self):
        rows = self._current_rows()
        direction = self._direction()
        preview = preview_changes(rows, limit=20, direction=direction)
        convert = self._convert_fn()
        total_changed = sum(1 for r in rows if convert(r.get("description", ""))[1] > 0)
        self.preview_table.setRowCount(0)
        for p in preview:
            row = self.preview_table.rowCount()
            self.preview_table.insertRow(row)
            self.preview_table.setItem(row, 0, QTableWidgetItem(str(p["point"])))
            self.preview_table.setItem(row, 1, QTableWidgetItem(p["before"]))
            self.preview_table.setItem(row, 2, QTableWidgetItem(p["after"]))
        suffix = f" (showing first {len(preview)})" if total_changed > len(preview) else ""
        self.summary_lbl.setText(f"{total_changed} rows will change{suffix}.")

    def apply_to_rows(self, rows):
        convert = self._convert_fn()
        for row in rows:
            new_desc, count = convert(row.get("description", ""))
            if count > 0:
                row["description"] = new_desc
        return rows
