"""Browse the code catalog."""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem


class CodeBrowser(QDialog):
    def __init__(self, codes, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Code Browser")
        layout = QVBoxLayout(self)
        table = QTableWidget(len(codes), 4, self)
        table.setHorizontalHeaderLabels(["Category", "Code", "Type", "Description"])
        for row, entry in enumerate(codes):
            for col, key in enumerate(("category", "code", "type", "description")):
                item = QTableWidgetItem(str(entry.get(key, "")))
                table.setItem(row, col, item)
        table.resizeColumnsToContents()
        layout.addWidget(table)
