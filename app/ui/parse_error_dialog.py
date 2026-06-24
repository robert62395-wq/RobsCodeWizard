"""Parse error summary dialog (v0.5.3.1)."""
from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog,
)


class ParseErrorDialog(QDialog):
    """Shown after a file parse finds errors. Lists the skipped rows."""
    
    def __init__(self, result, source_path=None, parent=None):
        super().__init__(parent)
        self._result = result
        self._source_path = source_path
        self.setWindowTitle("Parse warnings")
        self.setMinimumWidth(640)
        self.setMinimumHeight(400)
        
        layout = QVBoxLayout(self)
        
        summary = QLabel(
            f"<h3>Parse completed with warnings</h3>"
            f"<p><b>{len(result.rows)}</b> of <b>{result.total_lines}</b> rows "
            f"loaded successfully.<br>"
            f"<b>{len(result.errors)}</b> rows were skipped due to errors:</p>"
        )
        summary.setTextFormat(Qt.RichText)
        summary.setWordWrap(True)
        layout.addWidget(summary)
        
        table = QTableWidget(0, 3)
        table.setHorizontalHeaderLabels(["Line #", "Reason", "Raw content"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        table.horizontalHeader().setStretchLastSection(True)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        for err in result.errors:
            row = table.rowCount()
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(str(err.line_number)))
            table.setItem(row, 1, QTableWidgetItem(err.reason))
            table.setItem(row, 2, QTableWidgetItem(err.snippet))
        layout.addWidget(table)
        
        btn_row = QHBoxLayout()
        save_btn = QPushButton("Save error log...")
        save_btn.setToolTip("Save the list of skipped rows to a text file for review.")
        save_btn.clicked.connect(self._on_save_log)
        btn_row.addWidget(save_btn)
        btn_row.addStretch(1)
        ok_btn = QPushButton("Continue with loaded rows")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)
        btn_row.addWidget(ok_btn)
        layout.addLayout(btn_row)
    
    def _on_save_log(self):
        default_name = "parse_errors.txt"
        if self._source_path:
            from pathlib import Path
            default_name = Path(self._source_path).stem + "_parse_errors.txt"
        path, _ = QFileDialog.getSaveFileName(
            self, "Save parse error log", default_name, "Text (*.txt)"
        )
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(self._result.summary() + "\n\n")
            for err in self._result.errors:
                f.write(str(err) + "\n")