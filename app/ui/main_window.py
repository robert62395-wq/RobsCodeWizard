"""Main window (Phase 3: ODOT parser dispatch)."""
import logging, os
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox, QMenu, QHeaderView,
    QLabel,
)
from PySide6.QtGui import QColor, QAction, QDesktopServices
from PySide6.QtCore import Qt, QUrl

from app import __version__
from app.services.file_parser import parse_file
from app.services.validator import validate_rows
from app.services.suggester import build_suggestions
from app.services.catalog_loader import load_catalog
from app.services.linework_fix import run_linework_fix
from app.services.report_exporter import export_report
from app.services.settings import load_settings, set_setting
from app.services.updater import download_update, apply_update_hint
from app.services.logging_setup import get_log_dir, get_log_path, read_recent_log
from app.services import recovery
from app.ui.update_thread import UpdateCheckThread
from app.ui.log_viewer import LogViewerDialog
from app.ui.codeset_selector import CodeSetSelector
from app.ui.modified_data_tab import ModifiedDataTab


COLUMNS = ["Point number", "Original Description", "Edited Description",
           "Valid", "Issues/Warnings", "Notes", "Suggestion"]

log = logging.getLogger("robs_code_wizard")


def _p_sort_key(row):
    """Sort key: numeric P where possible, else lexical."""
    try:
        return (0, float(row.get("P", 0) or 0))
    except (TypeError, ValueError):
        return (1, str(row.get("P", "")))


class MainWindow(QMainWindow):
    def __init__(self, safe_mode=False):
        super().__init__()
        self.resize(1100, 650)
        self.safe_mode = safe_mode or os.environ.get("ROBS_CODE_WIZARD_SAFE") == "1"
        self.settings = load_settings()
        self.codeset = load_catalog(self.settings.get("active_codeset", "vdt"))
        self.rows = []; self.results = []; self.suggestions = []
        self.source_path = None
        self._update_thread = None; self._silent_check = True
        self._build_ui(); self._build_menu()
        self._sync_window_title()
        if not self.safe_mode:
            self._maybe_restore_session()
            if self.settings.get("check_on_startup", True):
                self._start_update_check(silent=True)

    def _sync_window_title(self):
        active = (self.codeset.name or "vdt").upper()
        self.setWindowTitle(f"Rob\'s Code Wizard - v{__version__} ({active})")

    def _build_ui(self):
        self.tabs = QTabWidget(); self.setCentralWidget(self.tabs)
        self.tabs.addTab(self._build_raw_data_tab(), "Raw Data")
        self.modified_tab = ModifiedDataTab(self)
        self.tabs.addTab(self.modified_tab, "Modified Data")

    def _build_menu(self):
        bar = self.menuBar()
        help_menu = bar.addMenu("&Help")
        check_action = QAction("Check for Updates...", self)
        check_action.triggered.connect(lambda: self._start_update_check(silent=False))
        help_menu.addAction(check_action)
        log_action = QAction("View Recent Log...", self)
        log_action.triggered.connect(self._show_log_viewer); help_menu.addAction(log_action)
        report_action = QAction("Report a Problem...", self)
        report_action.triggered.connect(self._open_log_folder); help_menu.addAction(report_action)
        help_menu.addSeparator()
        about_action = QAction("About", self); about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _build_raw_data_tab(self):
        page = QWidget(); layout = QVBoxLayout(page)
        bar = QHBoxLayout()
        bar.addWidget(QLabel("Code Set:"))
        self.codeset_selector = CodeSetSelector()
        self.codeset_selector.set_active(self.codeset.name)
        self.codeset_selector.codesetChanged.connect(self._on_codeset_changed)
        bar.addWidget(self.codeset_selector)
        bar.addSpacing(20)
        open_btn = QPushButton("Open CSV/TXT..."); open_btn.clicked.connect(self.on_open_file)
        linework_btn = QPushButton("Linework Fix"); linework_btn.clicked.connect(self.on_linework_fix)
        self.export_btn = QPushButton("Export Validation Report...")
        self.export_btn.clicked.connect(self.on_export_report); self.export_btn.setEnabled(False)
        bar.addWidget(open_btn); bar.addWidget(linework_btn); bar.addWidget(self.export_btn); bar.addStretch(1)
        layout.addLayout(bar)
        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        # v0.3.9.5.0.9: Raw Data is read-only - edits happen in the Modified Data tab
        layout.addWidget(self.table)
        return page

    def _on_codeset_changed(self, name: str):
        """v0.3.9.4.1: defer revalidation so the dropdown updates instantly."""
        try:
            log.info("Code set switching: %s -> %s", self.codeset.name, name)
            set_setting("active_codeset", name)
            self.settings["active_codeset"] = name
            self.codeset = load_catalog(name)
            if self.rows:
                from PySide6.QtCore import QTimer
                QTimer.singleShot(0, self._revalidate_and_repopulate)
        except Exception as exc:
            log.exception("Code set switch failed: %s", exc)
            self._error_dialog("Code set switch failed", exc)

    def _revalidate_and_repopulate(self):
        """v0.3.9.5.0.9: busy dialog + refresh Modified Data tab after revalidation."""
        try:
            if not self.rows:
                return
            from app.ui.busy_dialog import busy
            with busy(self, "Switching code set...") as dlg:
                self.results = validate_rows(self.rows, self.codeset)
                dlg.set_text("Building suggestions...")
                self.suggestions = build_suggestions(self.rows, self.codeset, self.results)
                dlg.set_text("Updating table...")
                self._populate_table()
                if hasattr(self, "modified_tab"):
                    self.modified_tab.refresh_from_parent()
        except Exception as exc:
            log.exception("Revalidation failed: %s", exc)
            self._error_dialog("Revalidation failed", exc)

    def on_open_file(self):
        try:
            path, _ = QFileDialog.getOpenFileName(self, "Select survey CSV/TXT", "",
                "Survey files (*.csv *.txt);;All files (*.*)")
            if not path: return
            self.source_path = path
            # Phase 3: dispatch to the right parser via the codeset
            self.rows = parse_file(path, self.codeset)
            # v0.3.9.5.0.9: sort by P (numeric where possible). Zero-elev rows are
            # kept and flagged yellow on both tabs - never auto-deleted.
            self.rows = sorted(self.rows, key=_p_sort_key)
            self.results = validate_rows(self.rows, self.codeset)
            self.suggestions = build_suggestions(self.rows, self.codeset, self.results)
            self._populate_table()
            if hasattr(self, "modified_tab"):
                self.modified_tab.refresh_from_parent()
            self.export_btn.setEnabled(bool(self.rows))
            if self.settings.get("auto_save_recovery", True):
                recovery.save_session(self.rows, source_path=path, suggestions=self.suggestions)
        except Exception as exc:
            log.exception("Failed to open file: %s", exc)
            self._error_dialog("Open failed", exc)

    def on_linework_fix(self):
        """Phase 4 (v0.3.9.4): show the Linework Fix overlay instead of a dialog."""
        try:
            if not self.rows:
                QMessageBox.information(self, "Linework Fix", "Open a file first.")
                return
            from app.ui.linework_fix_overlay import LineworkFixOverlay
            overlay = LineworkFixOverlay(self, self.rows, self.codeset)
            overlay.jumpToRow.connect(self._jump_to_row)
            overlay.show_overlay()
        except Exception as exc:
            log.exception("Linework fix failed: %s", exc)
            self._error_dialog("Linework Fix failed", exc)

    def _jump_to_row(self, row_index: int):
        """Select and scroll to the given row index in the Raw Data table."""
        if 0 <= row_index < self.table.rowCount():
            self.table.selectRow(row_index)
            cell = self.table.item(row_index, 0)
            if cell:
                self.table.scrollToItem(cell)

    def on_export_report(self):
        try:
            if not self.rows: return
            path, _ = QFileDialog.getSaveFileName(self, "Export Validation Report",
                "validation_report.xlsx", "Excel (*.xlsx);;Text (*.txt)")
            if not path: return
            out = export_report(self.rows, self.results, self.suggestions,
                                out_path=path, source_path=self.source_path)
            QMessageBox.information(self, "Validation Report", f"Report written to:\n{out}")
        except Exception as exc:
            log.exception("Export failed: %s", exc)
            self._error_dialog("Export failed", exc)

    def _error_dialog(self, title, exc):
        QMessageBox.critical(self, title,
            f"{exc}\n\nThe full error has been written to the log file.\n"
            "Use Help > View Recent Log... or Help > Report a Problem... to share it.")

    def _maybe_restore_session(self):
        if not recovery.has_session(): return
        data = recovery.load_session()
        if not data or not data.get("rows"): return
        reply = QMessageBox.question(self, "Restore Previous Session",
            f"A previous session was saved at:\n{data.get('saved_at', '(unknown)')}\n\n"
            f"Source: {data.get('source_path', '(unknown)')}\nRows: {len(data.get('rows', []))}\n\n"
            "Restore it now?", QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            recovery.clear_session(); return
        self.rows = data.get("rows", [])
        self.source_path = data.get("source_path")
        self.results = validate_rows(self.rows, self.codeset)
        self.suggestions = data.get("suggestions") or build_suggestions(self.rows, self.codeset, self.results)
        self.rows = sorted(self.rows, key=_p_sort_key)
        self._populate_table()
        if hasattr(self, "modified_tab"):
            self.modified_tab.refresh_from_parent()
        self.export_btn.setEnabled(bool(self.rows))

    def closeEvent(self, event):
        try:
            if self.rows and self.settings.get("auto_save_recovery", True):
                recovery.save_session(self.rows, source_path=self.source_path, suggestions=self.suggestions)
        except Exception as exc:
            log.exception("Failed to save recovery on close: %s", exc)
        super().closeEvent(event)

    def _start_update_check(self, silent):
        if self._update_thread is not None and self._update_thread.isRunning(): return
        url = self.settings.get("manifest_url")
        self._silent_check = silent
        self._update_thread = UpdateCheckThread(__version__, url, self)
        self._update_thread.result_ready.connect(self._on_update_result)
        self._update_thread.error.connect(self._on_update_error)
        self._update_thread.start()

    def _on_update_result(self, info):
        if info is None:
            if not self._silent_check:
                QMessageBox.information(self, "Check for Updates", "Could not reach the update server.")
            return
        if not info.is_newer:
            if not self._silent_check:
                QMessageBox.information(self, "Check for Updates", f"You\'re up to date (v{__version__}).")
            return
        reply = QMessageBox.question(self, "Update Available",
            f"A newer version is available: v{info.latest_version}\n\nDownload now?",
            QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes: return
        target = QFileDialog.getExistingDirectory(self, "Choose download folder", ".")
        if not target: return
        try:
            out = download_update(info, target)
            QMessageBox.information(self, "Update Downloaded", apply_update_hint(out))
        except Exception as exc:
            log.exception("Update download failed: %s", exc)
            self._error_dialog("Update Failed", exc)

    def _on_update_error(self, msg):
        if not self._silent_check:
            QMessageBox.warning(self, "Check for Updates", msg)

    def _show_log_viewer(self):
        dlg = LogViewerDialog(read_recent_log(), self); dlg.exec()

    def _open_log_folder(self):
        log_dir = get_log_dir(); log_dir.mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(log_dir)))
        QMessageBox.information(self, "Report a Problem",
            f"The log folder was opened:\n{log_dir}\n\nAttach \'{get_log_path().name}\' to your report.")

    def _show_about(self):
        QMessageBox.about(self, "About Rob\'s Code Wizard",
            f"<h3>Rob\'s Code Wizard</h3><p>Version <b>{__version__}</b></p>"
            "<p>Phase 3 of the v0.4.0 rollout - ODOT variable-attribute CSV parser.</p>"
            f"<p>Active code set: <b>{self.codeset.name.upper()}</b> ({len(self.codeset.codes)} codes).</p>")

    def _handle_zero_elevation_prompt(self):
        """v0.3.9.5.0.9: deprecated. Zero-elev rows are ALWAYS kept and flagged."""
        return

    def _populate_table(self):
        """v0.3.9.4.1: bulk-update guard (suppress repaints + sort) for big files."""
        from PySide6.QtWidgets import QApplication
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.table.setUpdatesEnabled(False)
        self.table.setSortingEnabled(False)
        try:
            self.table.setRowCount(len(self.rows))
            for i, row in enumerate(self.rows):
                result = self.results[i]
                suggestion = self.suggestions[i] or ""
                cells = [str(row.get("P", "")), str(row.get("D", "")), str(row.get("D", "")),
                         "Yes" if result["valid"] else "No",
                         "; ".join(result["issues"]), "", suggestion]
                for c, value in enumerate(cells):
                    item = QTableWidgetItem(value); item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(i, c, item)
                self._apply_row_color(i, row, result)
        finally:
            self.table.setSortingEnabled(True)
            self.table.setUpdatesEnabled(True)
            self.table.viewport().update()
            QApplication.restoreOverrideCursor()
        self.table.resizeColumnsToContents()

    def _apply_row_color(self, i, row, result):
        zero_elev = float(row.get("Z", 0) or 0) == 0.0
        bad_code = not result["valid"]
        color = None
        if bad_code: color = QColor("#ff6b6b")
        elif zero_elev: color = QColor("#fff3a0")
        if color:
            for c in range(self.table.columnCount()):
                cell = self.table.item(i, c)
                if cell: cell.setBackground(color)

    def _on_context_menu(self, pos):
        index = self.table.indexAt(pos)
        if not index.isValid(): return
        row = index.row()
        suggestion = self.suggestions[row] if row < len(self.suggestions) else None
        if not suggestion: return
        menu = QMenu(self)
        action = QAction(f"Apply suggestion: {suggestion}", self)
        action.triggered.connect(lambda: self._apply_suggestion(row, suggestion))
        menu.addAction(action)
        menu.exec(self.table.viewport().mapToGlobal(pos))

    def _apply_suggestion(self, row, suggestion):
        self.table.item(row, 2).setText(suggestion)
        self.rows[row]["D"] = suggestion
        self.results[row] = next(iter(validate_rows([self.rows[row]], self.codeset)))
        self._apply_row_color(row, self.rows[row], self.results[row])
