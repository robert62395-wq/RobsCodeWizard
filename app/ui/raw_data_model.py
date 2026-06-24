"""Raw Data table model (v0.5.4 performance rewrite).

QAbstractTableModel implementation that replaces the QTableWidget approach.
Populating becomes microseconds because Qt only asks for cell values via
data() when they're actually visible on-screen — no upfront cell creation.

Coloring is driven by Qt.BackgroundRole inside data(), keyed off the row's
validation result and elevation.
"""
from __future__ import annotations

from typing import List, Optional
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from PySide6.QtGui import QBrush, QColor

# Cached QColor + QBrush objects (created once, reused for every cell)
_RED_BRUSH = QBrush(QColor("#ff6b6b"))
_YELLOW_BRUSH = QBrush(QColor("#fff3a0"))
_CENTER_ALIGN = Qt.AlignmentFlag.AlignCenter

COLUMNS = [
    "Point number",
    "Original Description",
    "Edited Description",
    "Valid",
    "Issues/Warnings",
    "Notes",
    "Suggestion",
]


class RawDataTableModel(QAbstractTableModel):
    """Read-only model for the Raw Data tab.

    Holds three parallel lists: rows (parsed survey data), results (per-row
    validation), and suggestions (per-row suggestion strings or empty).
    All cell content is rendered on demand via data().
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rows: List[dict] = []
        self._results: List[dict] = []
        self._suggestions: List[str] = []

    # ---- Public API (replaces _populate_table) ----

    def set_data(self, rows, results, suggestions):
        """Replace all data in one atomic operation.

        Emits modelReset signal — Qt repaints only what's visible.
        Cost: microseconds regardless of row count.
        """
        self.beginResetModel()
        self._rows = list(rows or [])
        self._results = list(results or [])
        self._suggestions = list(suggestions or [])
        # Pad results/suggestions if caller gave us fewer than rows
        while len(self._results) < len(self._rows):
            self._results.append({"valid": True, "issues": []})
        while len(self._suggestions) < len(self._rows):
            self._suggestions.append("")
        self.endResetModel()

    def row_data(self, row_idx: int) -> Optional[dict]:
        """Return the underlying row dict for the given row index, or None."""
        if 0 <= row_idx < len(self._rows):
            return self._rows[row_idx]
        return None

    def result_data(self, row_idx: int) -> Optional[dict]:
        if 0 <= row_idx < len(self._results):
            return self._results[row_idx]
        return None

    def suggestion(self, row_idx: int) -> str:
        if 0 <= row_idx < len(self._suggestions):
            return self._suggestions[row_idx] or ""
        return ""

    def apply_suggestion(self, row_idx: int, suggestion: str):
        """Apply a suggestion to a single row's Edited Description.

        Updates the underlying row dict, then notifies the view to repaint
        only that row's affected cells.
        """
        if not (0 <= row_idx < len(self._rows)):
            return
        self._rows[row_idx]["D"] = suggestion
        # Notify view that columns 2 (Edited Description) and 6 (Suggestion) changed
        left = self.index(row_idx, 2)
        right = self.index(row_idx, 6)
        self.dataChanged.emit(left, right, [Qt.ItemDataRole.DisplayRole])

    def set_results(self, results):
        """Replace just the per-row results (e.g., after a revalidation).

        Does NOT touch rows or suggestions. Emits dataChanged for all rows
        on the Valid + Issues columns.
        """
        if not self._rows:
            return
        self._results = list(results or [])
        while len(self._results) < len(self._rows):
            self._results.append({"valid": True, "issues": []})
        # Notify everything redraws (background colors may have changed)
        top_left = self.index(0, 0)
        bottom_right = self.index(len(self._rows) - 1, len(COLUMNS) - 1)
        self.dataChanged.emit(top_left, bottom_right, [
            Qt.ItemDataRole.DisplayRole,
            Qt.ItemDataRole.BackgroundRole,
        ])

    def set_suggestions(self, suggestions):
        """Replace just the suggestions list."""
        if not self._rows:
            return
        self._suggestions = list(suggestions or [])
        while len(self._suggestions) < len(self._rows):
            self._suggestions.append("")
        top_left = self.index(0, 6)
        bottom_right = self.index(len(self._rows) - 1, 6)
        self.dataChanged.emit(top_left, bottom_right, [Qt.ItemDataRole.DisplayRole])

    # ---- QAbstractTableModel interface ----

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._rows)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(COLUMNS)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal and 0 <= section < len(COLUMNS):
            return COLUMNS[section]
        if orientation == Qt.Orientation.Vertical:
            return str(section + 1)
        return None

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        row = index.row()
        col = index.column()
        if not (0 <= row < len(self._rows)):
            return None

        if role == Qt.ItemDataRole.TextAlignmentRole:
            return int(_CENTER_ALIGN)

        if role == Qt.ItemDataRole.BackgroundRole:
            return self._row_brush(row)

        if role == Qt.ItemDataRole.DisplayRole:
            return self._cell_value(row, col)

        return None

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        # Read-only — edits happen via apply_suggestion() or external rewrite
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    # ---- Internals ----

    def _row_brush(self, row: int) -> Optional[QBrush]:
        """Return the cached QBrush for the row's color, or None for default."""
        row_dict = self._rows[row]
        result = self._results[row] if row < len(self._results) else None
        try:
            z = float(row_dict.get("Z", 0) or 0)
        except (TypeError, ValueError):
            z = 0.0
        bad_code = result is not None and not result.get("valid", True)
        if bad_code:
            return _RED_BRUSH
        if z == 0.0:
            return _YELLOW_BRUSH
        return None

    def _cell_value(self, row: int, col: int) -> str:
        row_dict = self._rows[row]
        result = self._results[row] if row < len(self._results) else {"valid": True, "issues": []}
        suggestion = self._suggestions[row] if row < len(self._suggestions) else ""

        if col == 0:  # Point number
            return str(row_dict.get("P", ""))
        if col == 1:  # Original Description
            return str(row_dict.get("D", ""))
        if col == 2:  # Edited Description
            return str(row_dict.get("D", ""))
        if col == 3:  # Valid
            return "Yes" if result.get("valid") else "No"
        if col == 4:  # Issues/Warnings
            return "; ".join(result.get("issues", []) or [])
        if col == 5:  # Notes
            return ""  # placeholder column, user-facing only
        if col == 6:  # Suggestion
            return suggestion
        return ""