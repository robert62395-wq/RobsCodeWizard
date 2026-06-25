from PySide6.QtCore import QAbstractTableModel, Qt
from PySide6.QtGui import QColor

COLUMNS = [
    "VDT Code", "VDT Description",
    "ODOT Code", "ODOT Description",
    "Confidence", "Count", "Notes"
]


class TranslationTableModel(QAbstractTableModel):
    def __init__(self, entries, used_counts):
        super().__init__()
        self.entries = entries
        self.used_counts = used_counts or {}

    def rowCount(self, parent=None):
        return len(self.entries)

    def columnCount(self, parent=None):
        return len(COLUMNS)

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return COLUMNS[section]
            return str(section + 1)

    def data(self, index, role):
        if not index.isValid():
            return None

        entry = self.entries[index.row()]
        vdt = entry.get("vdt") or {}
        odot = entry.get("odot") or {}
        conf = entry.get("confidence", "unmatched")

        values = [
            vdt.get("code", ""),
            vdt.get("description", ""),
            odot.get("code", ""),
            odot.get("description", ""),
            conf,
            "",
            entry.get("notes", ""),
        ]

        if role == Qt.DisplayRole:
            return str(values[index.column()])

        if role == Qt.BackgroundRole:
            if conf == "unmatched":
                return QColor("#ff6b6b")
            elif conf == "best-guess":
                return QColor("#d6b100")
            elif conf == "exact":
                return QColor("#6ecb63")
            elif conf == "manual":
                return QColor("#7aa2f7")

        return None