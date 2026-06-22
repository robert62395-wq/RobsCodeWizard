"""Export Tab - dialect-aware ODOT/VDT export (v0.4.7)."""
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
        self._refresh_for_dialect()

    def _build_ui(self):
        root = QVBoxLayout(self)

        self.dialect_lbl = QLabel("<i>Loading dialect info...</i>")
        root.addWidget(self.dialect_lbl)

        info = QLabel(
            "<h3>Export Survey Data</h3>"
            "<p>Export currently loaded rows to PNEZD CSV format. "
            "Grammar is selected automatically based on the active code set:</p>"
            "<ul>"
            "<li><b>VDT</b> &rarr; Civil3D uses VDT grammar (B, E, BC, EC, CLS)</li>"
            "<li><b>ODOT</b> &rarr; Civil3D uses ODOT alphabetic (BL*, EL*, OC*, CL*)</li>"
            "<li><b>ODOT</b> &rarr; OpenRoads uses ODOT numeric (1, 2, 3, 4) by default</li>"
            "</ul>"
            "<p><b>Note:</b> No header row is written. P, N, E, Z are never touched.</p>"
        )
        info.setWordWrap(True)
        root.addWidget(info)

        c3d_box = QGroupBox("Civil3D Export")
        c3d_layout = QVBoxLayout(c3d_box)
        self.c3d_desc = QLabel("")
        self.c3d_desc.setWordWrap(True)
        c3d_layout.addWidget(self.c3d_desc)
        self.c3d_export_btn = QPushButton("Export to Civil3D...")
        self.c3d_export_btn.clicked.connect(self._on_export_civil3d)
        c3d_layout.addWidget(self.c3d_export_btn)
        root.addWidget(c3d_box)

        or_box = QGroupBox("OpenRoads Export")
        or_layout = QVBoxLayout(or_box)
        self.or_desc = QLabel("")
        self.or_desc.setWordWrap(True)
        or_layout.addWidget(self.or_desc)
        self.or_use_numeric = QCheckBox("Use numeric line-connect codes (recommended for OpenRoads)")
        self.or_use_numeric.setChecked(True)
        or_layout.addWidget(self.or_use_numeric)
        self.or_export_btn = QPushButton("Export to OpenRoads...")
        self.or_export_btn.clicked.connect(self._on_export_openroads)
        or_layout.addWidget(self.or_export_btn)
        root.addWidget(or_box)

        root.addStretch(1)

    def _active_dialect(self):
        parent = self._parent_main
        if parent is None:
            return "odot"
        cs = getattr(parent, "codeset", None)
        if cs is None:
            return "odot"
        return str(getattr(cs, "name", "odot")).lower()

    def _refresh_for_dialect(self):
        dialect = self._active_dialect()
        if dialect == "vdt":
            self.dialect_lbl.setText("<b>Active code set: VDT</b>")
            self.c3d_desc.setText(
                "Output: VDT grammar (B, E, BC, EC, CLS).<br>"
                "Any ODOT-flavored tokens are normalized to VDT letters."
            )
            self.c3d_export_btn.setText("Export to Civil3D (VDT grammar)...")
            self.c3d_export_btn.setEnabled(True)
            self.or_desc.setText(
                "<i>VDT export to OpenRoads is not supported. "
                "Translate to ODOT via the Translation tab first.</i>"
            )
            self.or_export_btn.setEnabled(False)
            self.or_use_numeric.setEnabled(False)
            self.or_export_btn.setToolTip(
                "VDT export is Civil3D only. Translate to ODOT via Translation tab."
            )
        else:
            self.dialect_lbl.setText("<b>Active code set: ODOT</b>")
            self.c3d_desc.setText(
                "Output: ODOT alphabetic (BL*, EL*, OC*, CL*).<br>"
                "Numeric line-connect codes auto-convert to alphabetic."
            )
            self.c3d_export_btn.setText("Export to Civil3D (ODOT alphabetic)...")
            self.c3d_export_btn.setEnabled(True)
            self.or_desc.setText(
                "Output: ODOT numeric (1, 2, 3, 4) by default. "
                "Uncheck to keep alphabetic."
            )
            self.or_export_btn.setText("Export to OpenRoads...")
            self.or_export_btn.setEnabled(True)
            self.or_use_numeric.setEnabled(True)
            self.or_export_btn.setToolTip("")

    def showEvent(self, event):
        self._refresh_for_dialect()
        super().showEvent(event)

    def _check_rows(self):
        parent = self._parent_main
        if parent is None or not hasattr(parent, "rows") or not parent.rows:
            QMessageBox.information(
                self, "Export",
                "No rows loaded. Open a CSV/TXT file on the Raw Data tab first."
            )
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
        rows = self._check_rows()
        if rows is None:
            return
        dialect = self._active_dialect()
        if dialect == "vdt":
            from app.services.odot_exporter import export_vdt_to_civil3d as exporter
            suffix = "VDT_Civil3D"
            grammar_label = "VDT"
        else:
            from app.services.odot_exporter import export_odot_to_civil3d as exporter
            suffix = "ODOT_Civil3D"
            grammar_label = "ODOT alphabetic"
        path, _ = QFileDialog.getSaveFileName(
            self, "Export to Civil3D", self._suggest_filename(suffix),
            "CSV (*.csv);;All Files (*.*)"
        )
        if not path:
            return
        try:
            written, conversions = exporter(rows, Path(path))
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))
            return
        QMessageBox.information(
            self, "Civil3D Export Complete",
            f"Wrote {written} rows to:\n{path}\n\n"
            f"Grammar: {grammar_label}\n"
            f"Line-connect conversions: {conversions}"
        )

    def _on_export_openroads(self):
        rows = self._check_rows()
        if rows is None:
            return
        if self._active_dialect() == "vdt":
            QMessageBox.warning(
                self, "Not Supported",
                "VDT export to OpenRoads is not supported.\n\n"
                "Translate to ODOT via the Translation tab first."
            )
            return
        from app.services.odot_exporter import export_odot_to_openroads
        path, _ = QFileDialog.getSaveFileName(
            self, "Export to OpenRoads", self._suggest_filename("ODOT_OpenRoads"),
            "CSV (*.csv);;All Files (*.*)"
        )
        if not path:
            return
        try:
            written, conversions = export_odot_to_openroads(
                rows, Path(path), use_numeric=self.or_use_numeric.isChecked()
            )
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))
            return
        grammar = "numeric" if self.or_use_numeric.isChecked() else "alphabetic"
        QMessageBox.information(
            self, "OpenRoads Export Complete",
            f"Wrote {written} rows to:\n{path}\n\n"
            f"Grammar: ODOT {grammar}\n"
            f"Line-connect conversions: {conversions}"
        )
