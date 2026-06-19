"""Linework Fix audit dialog - Phase 4 of v0.4.0 rollout."""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QPushButton, QFileDialog, QHeaderView,
    QMessageBox, QGroupBox,
)
from PySide6.QtGui import QColor, QFont, QGuiApplication
from PySide6.QtCore import Signal

from app.services.linework_fix import (
    audit_with_locations, suggest_fix,
    export_audit_txt, export_audit_xlsx,
)


class LineworkFixDialog(QDialog):
    """Modal dialog showing the linework balance audit with navigation."""

    jumpToRow = Signal(int)

    def __init__(self, rows, codeset, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Linework Fix Audit")
        self.resize(720, 520)
        self._rows = rows
        self._codeset = codeset
        self._audit = audit_with_locations(rows, codeset)
        self._build_ui()

    def _grammar(self):
        return self._codeset.linework_grammar if self._codeset else None

    def _build_ui(self):
        layout = QVBoxLayout(self)
        cs_name = (self._codeset.name if self._codeset else "?").upper()
        total = self._audit.get("total_commands", 0)
        hdr = QLabel(f"Linework Fix - {cs_name} grammar | Total commands: {total}")
        f = QFont()
        f.setBold(True)
        hdr.setFont(f)
        layout.addWidget(hdr)

        unbal = self._audit.get("unbalanced", {})
        if unbal:
            grp = QGroupBox(f"Unbalanced Codes ({len(unbal)})")
            gl = QVBoxLayout(grp)
            tbl = QTableWidget(len(unbal), 6, self)
            tbl.setHorizontalHeaderLabels(
                ["Code", "Begins", "Ends", "Delta", "Suggestion", "Go to Row"]
            )
            tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            for i, (code, delta) in enumerate(sorted(unbal.items())):
                b = self._audit["begins"].get(code, 0)
                e = self._audit["ends"].get(code, 0)
                sug = suggest_fix(code, delta, self._grammar())
                tbl.setItem(i, 0, QTableWidgetItem(code))
                tbl.setItem(i, 1, QTableWidgetItem(str(b)))
                tbl.setItem(i, 2, QTableWidgetItem(str(e)))
                tbl.setItem(i, 3, QTableWidgetItem(f"{delta:+d}"))
                tbl.setItem(i, 4, QTableWidgetItem(sug))
                for c in range(5):
                    item = tbl.item(i, c)
                    if item:
                        item.setBackground(QColor("#ffcccc"))
                idxs = self._audit.get("row_indices", {}).get(code, [])
                btn = QPushButton("Go" if idxs else "-")
                btn.setEnabled(bool(idxs))
                if idxs:
                    first = idxs[0]
                    btn.clicked.connect(lambda _, r=first: self.jumpToRow.emit(r))
                tbl.setCellWidget(i, 5, btn)
            gl.addWidget(tbl)
            layout.addWidget(grp)
        else:
            ok = QLabel("All linework commands are balanced.")
            ok.setStyleSheet("color: green; font-weight: bold; padding: 8px;")
            layout.addWidget(ok)

        bal_codes = sorted(
            set(self._audit.get("begins", {})) | set(self._audit.get("ends", {}))
        )
        bal_codes = [c for c in bal_codes if c not in unbal]
        if bal_codes:
            self._bal_grp = QGroupBox(f"Balanced Codes ({len(bal_codes)})")
            self._bal_grp.setCheckable(True)
            self._bal_grp.setChecked(False)
            bgl = QVBoxLayout(self._bal_grp)
            btbl = QTableWidget(len(bal_codes), 3, self)
            btbl.setHorizontalHeaderLabels(["Code", "Begins", "Ends"])
            btbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            for i, code in enumerate(bal_codes):
                btbl.setItem(i, 0, QTableWidgetItem(code))
                btbl.setItem(i, 1, QTableWidgetItem(str(self._audit["begins"].get(code, 0))))
                btbl.setItem(i, 2, QTableWidgetItem(str(self._audit["ends"].get(code, 0))))
            bgl.addWidget(btbl)
            self._bal_grp.toggled.connect(btbl.setVisible)
            btbl.setVisible(False)
            layout.addWidget(self._bal_grp)

        layout.addStretch(1)
        bar = QHBoxLayout()
        copy_btn = QPushButton("Copy Summary")
        copy_btn.clicked.connect(self._copy_summary)
        txt_btn = QPushButton("Export TXT...")
        txt_btn.clicked.connect(self._export_txt)
        xlsx_btn = QPushButton("Export XLSX...")
        xlsx_btn.clicked.connect(self._export_xlsx)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        bar.addWidget(copy_btn)
        bar.addWidget(txt_btn)
        bar.addWidget(xlsx_btn)
        bar.addStretch(1)
        bar.addWidget(close_btn)
        layout.addLayout(bar)

    def _build_summary_text(self):
        a = self._audit
        cs = (self._codeset.name if self._codeset else "?").upper()
        lines = [
            f"Linework Fix Audit - {cs} grammar",
            f"Total commands  : {a.get('total_commands', 0)}",
            f"Codes w/ begins : {len(a.get('begins', {}))}",
            f"Codes w/ ends   : {len(a.get('ends', {}))}",
            f"Unbalanced      : {len(a.get('unbalanced', {}))}",
        ]
        if a.get("unbalanced"):
            lines.append("")
            lines.append("Unbalanced codes:")
            for code, delta in a["unbalanced"].items():
                lines.append(f"  {code}: {delta:+d}")
        return "\n".join(lines)

    def _copy_summary(self):
        QGuiApplication.clipboard().setText(self._build_summary_text())
        QMessageBox.information(self, "Copied", "Summary copied to clipboard.")

    def _export_txt(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export TXT", "linework_audit.txt", "Text (*.txt)"
        )
        if not path:
            return
        try:
            out = export_audit_txt(self._audit, path)
            QMessageBox.information(self, "Exported", f"Wrote {out}")
        except Exception as exc:
            QMessageBox.critical(self, "Export failed", str(exc))

    def _export_xlsx(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export XLSX", "linework_audit.xlsx", "Excel (*.xlsx)"
        )
        if not path:
            return
        try:
            out = export_audit_xlsx(self._audit, path, self._grammar())
            QMessageBox.information(self, "Exported", f"Wrote {out}")
        except Exception as exc:
            QMessageBox.critical(self, "Export failed", str(exc))