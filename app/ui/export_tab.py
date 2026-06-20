"""Export Tab - ODOT export for Civil3D and OpenRoads (v0.4.5)."""
from __future__ import annotations
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton, QLabel,
    QFileDialog, QMessageBox, QCheckBox,
)


class ExportTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._parent_main = parent
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        info = QLabel(
            "<h3>Export Survey Data</h3>"
            "<p>Export currently loaded rows to PNEZD CSV format.</p>"
            "<p><b>Civil3D</b> requires alphabetic line-connect codes (BL*, EL*, OC*, CL*).<br>"
            "<b>OpenRoads</b> typically uses numeric line-connect codes (1, 2, 3, 4) "
            "but accepts alphabetic as well.</p>"
            "<p><b>Note:</b> No header row is written (AutoCAD/Civil3D requirement).</p>"
        )
        info.setWordWrap(True)
        root.addWidget(info)

        c3d_box = QGroupBox("Civil3D Export")
        c3d_layout = QVBoxLayout(c3d_box)
        c3d_desc = QLabel("Output: PNEZD CSV, no header, alphabetic line-connect codes only.")
        c3d_desc.setWordWrap(True)
        c3d_layout.addWidget(c3d_desc)
        self.c3d_export_btn = QPushButton("Export to Civil3D...")
        self.c3d_export_btn.clicked.connect(self._on_export_civil3d)
        c3d_layout.addWidget(self.c3d_export_btn)
        root.addWidget(c3d_box)

        or_box = QGroupBox("OpenRoads Export")
        or_layout = QVBoxLayout(or_box)
        or_desc = QLabel("Output: PNEZD CSV, no header. Line-connect codes converted to numeric by default.")
        or_desc.setWordWrap(True)
        or_layout.addWidget(or_desc)
        self.or_use_numeric = QCheckBox("Convert line-connect codes to numeric (for OpenRoads field crews)")
        self.or_use_numeric.setChecked(True)
        or_layout.addWidget(self.or_use_numeric)
        self.or_export_btn = QPushButton("Export to OpenRoads...")
        self.or_export_btn.clicked.connect(self._on_export_openroads)
        or_layout.addWidget(self.or_export_btn)
        root.addWidget(or_box)
        root.addStretch(1)

    def _check_rows(self):
        parent = self._parent_main
        if parent is None or not hasattr(parent, "rows") or not parent.rows:
            QMessageBox.information(self, "Export", "No rows loaded. Open a CSV/TXT file on the Raw Data tab first.")
            return None
        return parent.rows

    def _suggest_filename(self, suffix):
        parent = self._parent_main
        src = getattr(parent, "source_path", None) if parent else None
        if src:
            stem = Path(src).stem
            return f"{stem}_{suffix}.csv"
        return f"export_{suffix}.csv"

    def _on_export_civil3d(self):
        from app.services.odot_exporter import export_civil3d
        rows = self._check_rows()
        if rows is None:
            return
        suggested = self._suggest_filename("ODOT_Civil3D")
        path, _ = QFileDialog.getSaveFileName(self, "Export to Civil3D", suggested, "CSV (*.csv);;All Files (*.*)")
        if not path:
            return
        try:
            written, conversions = export_civil3d(rows, Path(path))
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))
            return
        QMessageBox.information(
            self, "Civil3D Export Complete",
            f"Wrote {written} rows to:\n{path}\n\nNumeric -> alphabetic conversions: {conversions}"
        )

    def _on_export_openroads(self):
        from app.services.odot_exporter import export_openroads
        rows = self._check_rows()
        if rows is None:
            return
        suggested = self._suggest_filename("ODOT_OpenRoads")
        path, _ = QFileDialog.getSaveFileName(self, "Export to OpenRoads", suggested, "CSV (*.csv);;All Files (*.*)")
        if not path:
            return
        try:
            written, conversions = export_openroads(rows, Path(path), use_numeric=self.or_use_numeric.isChecked())
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))
            return
        QMessageBox.information(
            self, "OpenRoads Export Complete",
            f"Wrote {written} rows to:\n{path}\n\nAlphabetic -> numeric conversions: {conversions}"
        )
