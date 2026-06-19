"""Linework Fix overlay - Phase 4 of v0.3.9.4 rollout.

Embedded PySide6 panel that overlays the main window instead of opening
as a separate QDialog.  Preserves all behavior of LineworkFixDialog:
audit table, balanced-codes group, Copy / Export TXT / Export XLSX,
and a "jump to row" signal for the parent.
"""
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QPushButton, QFileDialog, QHeaderView,
    QMessageBox, QGroupBox, QGraphicsDropShadowEffect, QSizePolicy,
)
from PySide6.QtGui import QColor, QFont, QGuiApplication, QKeySequence, QShortcut
from PySide6.QtCore import Qt, Signal, QEvent

from app.services.linework_fix import (
    audit_with_locations, suggest_fix,
    export_audit_txt, export_audit_xlsx,
)


class _Dim(QFrame):
    """Semi-transparent dim layer behind the overlay panel."""
    clicked = Signal()

    def __init__(self, parent):
        super().__init__(parent)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 110);")
        self.setAttribute(Qt.WA_StyledBackground, True)

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


class LineworkFixOverlay(QFrame):
    """In-window overlay replacement for LineworkFixDialog.

    Lifecycle:
        overlay = LineworkFixOverlay(parent_main_window, rows, codeset)
        overlay.jumpToRow.connect(main_window._jump_to_row)
        overlay.show_overlay()
    """

    jumpToRow = Signal(int)
    closed = Signal()

    PANEL_WIDTH_RATIO = 0.78
    PANEL_HEIGHT_RATIO = 0.82

    def __init__(self, parent, rows, codeset):
        super().__init__(parent)
        self._parent_widget = parent
        self._rows = rows
        self._codeset = codeset
        self._audit = audit_with_locations(rows, codeset)
        self._dim = None

        self.setObjectName("LineworkFixOverlay")
        self.setStyleSheet("""
            QFrame#LineworkFixOverlay {
                background-color: #ffffff;
                border: 1px solid #d1d5db;
                border-radius: 10px;
            }
            QPushButton#PrimaryBtn {
                background-color: #2563eb;
                color: white;
                padding: 6px 14px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton#PrimaryBtn:hover { background-color: #1d4ed8; }
            QLabel#HeaderLbl { color: #1f2937; }
            QLabel#OkLbl { color: #16a34a; font-weight: bold; padding: 8px; }
            QLabel#VersionLbl { color: #9ca3af; }
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 110))
        self.setGraphicsEffect(shadow)

        self._build_ui()
        self._install_parent_filter()
        self._register_shortcuts()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def show_overlay(self):
        if self._dim is None:
            self._dim = _Dim(self._parent_widget)
            self._dim.clicked.connect(self.close_overlay)
            self._dim.show()
            self._dim.raise_()
        self._reposition()
        self.show()
        self.raise_()
        self.setFocus(Qt.OtherFocusReason)

    def close_overlay(self):
        if self._dim is not None:
            self._dim.deleteLater()
            self._dim = None
        self.closed.emit()
        self._uninstall_parent_filter()
        self.deleteLater()

    # ------------------------------------------------------------------
    # Layout / positioning
    # ------------------------------------------------------------------
    def _reposition(self):
        if self._parent_widget is None:
            return
        pw = self._parent_widget.width()
        ph = self._parent_widget.height()
        if self._dim is not None:
            self._dim.setGeometry(0, 0, pw, ph)
        w = max(560, int(pw * self.PANEL_WIDTH_RATIO))
        h = max(420, int(ph * self.PANEL_HEIGHT_RATIO))
        x = max(0, (pw - w) // 2)
        y = max(0, (ph - h) // 2)
        self.setGeometry(x, y, w, h)

    def _install_parent_filter(self):
        if self._parent_widget is not None:
            self._parent_widget.installEventFilter(self)

    def _uninstall_parent_filter(self):
        if self._parent_widget is not None:
            self._parent_widget.removeEventFilter(self)

    def eventFilter(self, obj, event):
        if obj is self._parent_widget and event.type() == QEvent.Resize:
            self._reposition()
        return super().eventFilter(obj, event)

    def _register_shortcuts(self):
        QShortcut(QKeySequence("Escape"), self, activated=self.close_overlay)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _grammar(self):
        return self._codeset.linework_grammar if self._codeset else None

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(10)

        hdr_row = QHBoxLayout()
        cs_name = (self._codeset.name if self._codeset else "?").upper()
        total = self._audit.get("total_commands", 0)
        hdr = QLabel(f"Linework Fix - {cs_name} grammar | Total commands: {total}")
        hdr.setObjectName("HeaderLbl")
        f = QFont(); f.setBold(True); f.setPointSize(11)
        hdr.setFont(f)
        hdr_row.addWidget(hdr)
        hdr_row.addStretch(1)

        ver = QLabel("v0.3.9.4")
        ver.setObjectName("VersionLbl")
        hdr_row.addWidget(ver)
        layout.addLayout(hdr_row)

        unbal = self._audit.get("unbalanced", {})
        if unbal:
            grp = QGroupBox(f"Unbalanced Codes ({len(unbal)})")
            gl = QVBoxLayout(grp)
            tbl = QTableWidget(len(unbal), 6, self)
            tbl.setHorizontalHeaderLabels(
                ["Code", "Begins", "Ends", "Delta", "Suggestion", "Go to Row"]
            )
            tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            tbl.verticalHeader().setVisible(False)
            tbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
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
                    btn.clicked.connect(lambda _, r=first: self._jump_and_close(r))
                tbl.setCellWidget(i, 5, btn)
            gl.addWidget(tbl)
            layout.addWidget(grp, 1)
        else:
            ok = QLabel("All linework commands are balanced.")
            ok.setObjectName("OkLbl")
            ok.setAlignment(Qt.AlignCenter)
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
            btbl.verticalHeader().setVisible(False)
            for i, code in enumerate(bal_codes):
                btbl.setItem(i, 0, QTableWidgetItem(code))
                btbl.setItem(i, 1, QTableWidgetItem(str(self._audit["begins"].get(code, 0))))
                btbl.setItem(i, 2, QTableWidgetItem(str(self._audit["ends"].get(code, 0))))
            bgl.addWidget(btbl)
            self._bal_grp.toggled.connect(btbl.setVisible)
            btbl.setVisible(False)
            layout.addWidget(self._bal_grp)

        layout.addStretch(0)

        bar = QHBoxLayout()
        copy_btn = QPushButton("Copy Summary")
        copy_btn.clicked.connect(self._copy_summary)
        txt_btn = QPushButton("Export TXT...")
        txt_btn.clicked.connect(self._export_txt)
        xlsx_btn = QPushButton("Export XLSX...")
        xlsx_btn.clicked.connect(self._export_xlsx)
        close_btn = QPushButton("Close")
        close_btn.setObjectName("PrimaryBtn")
        close_btn.clicked.connect(self.close_overlay)

        bar.addWidget(copy_btn)
        bar.addWidget(txt_btn)
        bar.addWidget(xlsx_btn)
        bar.addStretch(1)
        bar.addWidget(close_btn)
        layout.addLayout(bar)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def _jump_and_close(self, row_index):
        self.jumpToRow.emit(int(row_index))
        self.close_overlay()

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
