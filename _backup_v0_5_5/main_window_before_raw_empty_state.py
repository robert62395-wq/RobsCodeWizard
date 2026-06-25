# v0.5.3 diag logs downgraded - markers moved from INFO to DEBUG
"""Main window (Phase 3: ODOT parser dispatch).

v0.4.2 integration:
    - Translation tab inserted between Raw Data and Modified Data
    - Tools > Convert Line Connect Codes... action added to existing Tools menu
"""
import logging, os
from pathlib import Path
from app.ui.help_icon import HelpIcon
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QTableView, QFileDialog, QMessageBox, QMenu, QHeaderView,
    QLabel,
)
from PySide6.QtGui import QColor, QAction, QDesktopServices
from PySide6.QtCore import Qt, QUrl
from app import __version__
from app.services.file_parser import parse_file
from app.services.file_parser import parse_file_with_errors  # v0.5.3.3
from app.services.recovery_timer import RecoveryTimer  # v0.5.3.3
from app.ui.parse_error_dialog import ParseErrorDialog  # v0.5.3.3
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
from app.ui.raw_data_model import RawDataTableModel  # v0.5.4 model/view
# v0.4.2: Phase 2 Translation tab + Convert Line Connect Codes dialog
from app.ui.translation_tab import TranslationTab
from app.ui.convert_line_connect_dialog import ConvertLineConnectDialog
# v0.5.2 status bar + help icons
from app.services.status_bar_helper import format_permanent_status
from app.ui.help_icon import HelpIcon

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
            # v0.5.3.3 wireup: auto-save recovery timer
        try:
            self._recovery_timer = RecoveryTimer(self)
            self._recovery_timer.set_save_callback(
                lambda: recovery.save_session(
                    self.rows,
                    source_path=self.source_path,
                    suggestions=self.suggestions,
                )
            )
            if self.settings.get("auto_save_recovery", True):
                self._recovery_timer.start()
        except Exception as exc:
            log.exception("RecoveryTimer init failed: %s", exc)
            self._recovery_timer = None
        if self.settings.get("check_on_startup", True):
                self._start_update_check(silent=True)

    def _sync_window_title(self):
        active = (self.codeset.name or "vdt").upper()
        self.setWindowTitle(f"Rob's Code Wizard - v{__version__} ({active})")

    def _build_ui(self):
        self.tabs = QTabWidget(); self.setCentralWidget(self.tabs)
        self.tabs.addTab(self._build_raw_data_tab(), "Raw Data")
        # v0.4.2: Translation tab between Raw Data and Modified Data
        self.translation_tab = TranslationTab(self)
        self.tabs.addTab(self.translation_tab, "Translation")
        self.modified_tab = ModifiedDataTab(self)
        self.tabs.addTab(self.modified_tab, "Modified Data")
        # v0.5.2 status bar init
        self._status = self.statusBar()
        self._status.show()
        self._status.showMessage("Ready")

    def _build_menu(self):
        bar = self.menuBar()
        # v0.3.9.5.2.0.1: Tools menu for point/elevation offset utilities
        tools_menu = bar.addMenu("&Tools")
        self._point_offset_action = QAction("Apply Point Offset...", self)
        self._point_offset_action.triggered.connect(self._on_apply_point_offset)
        self._point_offset_action.setEnabled(False)
        tools_menu.addAction(self._point_offset_action)
        self._elev_offset_action = QAction("Apply Elevation Offset...", self)
        self._elev_offset_action.triggered.connect(self._on_apply_elevation_offset)
        self._elev_offset_action.setEnabled(False)
        tools_menu.addAction(self._elev_offset_action)
        tools_menu.addSeparator()
        self._undo_offset_action = QAction("Undo Last Offset", self)
        self._undo_offset_action.triggered.connect(self._on_undo_offset)
        self._undo_offset_action.setEnabled(False)
        tools_menu.addAction(self._undo_offset_action)
        # v0.4.2: Convert Line Connect Codes (numeric -> alphabetic, Civil3D)
        tools_menu.addSeparator()
        self._convert_lc_action = QAction("Convert Line Connect Codes...", self)
        self._convert_lc_action.triggered.connect(self._on_convert_line_connect)
        self._convert_lc_action.setEnabled(False)
        tools_menu.addAction(self._convert_lc_action)

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
        help_menu.addSeparator()
        # v0.3.9.5.1.6: placeholder reserved for future capability
        dnt_action = QAction("DO NOT TOUCH", self)
        dnt_action.triggered.connect(self._on_do_not_touch)
        help_menu.addAction(dnt_action)

    def _build_raw_data_tab(self):
        """Build the Raw Data tab.

        v0.5.4 model/view rewrite:
        QTableWidget is replaced by QTableView + RawDataTableModel.
        """
        page = QWidget()
        layout = QVBoxLayout(page)

        bar = QHBoxLayout()
        bar.addWidget(QLabel("Code Set:"))

        self.codeset_selector = CodeSetSelector()
        self.codeset_selector.set_active(self.codeset.name)
        self.codeset_selector.codesetChanged.connect(self._on_codeset_changed)

        bar.addWidget(self.codeset_selector)
        bar.addWidget(HelpIcon("code_set"))

        bar.addSpacing(20)

        open_btn = QPushButton("Open CSV/TXT...")
        open_btn.setToolTip("Load a PNEZD CSV or TXT point file for analysis.")
        open_btn.clicked.connect(self.on_open_file)

        linework_btn = QPushButton("Linework Fix")
        linework_btn.setToolTip("Open the Linework Fix overlay to find and repair linework grammar problems.")
        linework_btn.clicked.connect(self.on_linework_fix)

        self.export_btn = QPushButton("Export Validation Report...")
        self.export_btn.setToolTip("Export validation results, issues, notes, and suggestions to a report.")
        self.export_btn.clicked.connect(self.on_export_report)
        self.export_btn.setEnabled(False)

        bar.addWidget(open_btn)
        bar.addWidget(linework_btn)
        bar.addWidget(HelpIcon("linework_fix"))
        bar.addWidget(self.export_btn)
        bar.addStretch(1)

        layout.addLayout(bar)

        # v0.5.4 model/view: QTableView + RawDataTableModel
        self.raw_data_model = RawDataTableModel(self)
        self.table = QTableView(page)
        self.table.setModel(self.raw_data_model)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(False)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._on_context_menu)

        # v0.3.9.5.0.9: Raw Data is read-only - edits happen in the Modified Data tab
        layout.addWidget(self.table)
        return page

    def _on_codeset_changed(self, name):
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
        """v0.3.9.5.2.0.1 diagnostic: timing logs around the QThread worker dispatch."""
        try:
            if not self.rows:
                return
            import time as _t
            self._reval_t0 = _t.perf_counter()
            log.debug("[diag] _revalidate_and_repopulate: spawning worker (%d rows)", len(self.rows))
            from app.ui.busy_dialog import BusyDialog
            from app.services.revalidation_worker import RevalidationWorker
            self._reval_dlg = BusyDialog(self, "Switching code set...")
            self._reval_dlg.show()
            self._reval_worker = RevalidationWorker(self.rows, self.codeset, self)
            self._reval_worker.stage.connect(self._reval_dlg.set_text)
            self._reval_worker.finished_with_data.connect(self._on_revalidation_done)
            self._reval_worker.error_message.connect(self._on_revalidation_error)
            self._reval_worker.start()
            log.debug("[diag] worker.start() called, returning to event loop")
        except Exception as exc:
            log.exception("Revalidation failed: %s", exc)
            self._error_dialog("Revalidation failed", exc)

    def _on_revalidation_done(self, results, suggestions):
        """v0.3.9.5.2.0.1 diagnostic: timing logs around table repopulation."""
        import time as _t
        t0 = _t.perf_counter()
        log.debug("[diag] _on_revalidation_done: entry (received %d results)", len(results))
        self.results = results
        self.suggestions = suggestions
        t1 = _t.perf_counter()
        self._populate_table()
        t2 = _t.perf_counter()
        log.debug("[diag] _populate_table: %.3fs (Raw Data, %d rows)", t2 - t1, len(self.rows))
        if hasattr(self, "modified_tab"):
            t3 = _t.perf_counter()
            self.modified_tab.refresh_from_parent()
            t4 = _t.perf_counter()
            log.debug("[diag] modified_tab.refresh_from_parent: %.3fs", t4 - t3)
        if hasattr(self, "_reval_dlg") and self._reval_dlg:
            self._reval_dlg.close()
            self._reval_dlg = None
        t5 = _t.perf_counter()
        log.debug("[diag] _on_revalidation_done total: %.3fs", t5 - t0)
        if hasattr(self, "_reval_t0"):
            log.debug("[diag] end-to-end code-set switch: %.3fs", t5 - self._reval_t0)
            self._update_status_bar()  # v0.5.2.3
            if getattr(self, '_recovery_timer', None) is not None:
                self._recovery_timer.mark_dirty()  # v0.5.3.3 wireup
            
    def _on_revalidation_error(self, msg):
        """v0.3.9.5.1.6: revalidation worker raised."""
        if hasattr(self, "_reval_dlg") and self._reval_dlg:
            self._reval_dlg.close()
            self._reval_dlg = None
        log.error("Revalidation worker failed: %s", msg)
        self._error_dialog("Revalidation failed", Exception(msg))

    def on_open_file(self):
        try:
            path, _ = QFileDialog.getOpenFileName(self, "Select survey CSV/TXT", "",
                "Survey files (*.csv *.txt);;All files (*.*)")
            if not path: return
            self.source_path = path
            # Phase 3: dispatch to the right parser via the codeset
            # v0.5.3.3 wireup: collect parse errors and show dialog if any
            _parse_result = parse_file_with_errors(path, self.codeset)
            self.rows = _parse_result.rows
            if _parse_result.has_errors:
                try:
                    _dlg = ParseErrorDialog(_parse_result, source_path=path, parent=self)
                    _dlg.exec()
                except Exception as exc:
                    log.exception("ParseErrorDialog failed: %s", exc)
            # v0.3.9.5.0.9: sort by P (numeric where possible). Zero-elev rows are
            # kept and flagged yellow on both tabs - never auto-deleted.
            self.rows = sorted(self.rows, key=_p_sort_key)
            self.results = validate_rows(self.rows, self.codeset)
            self.suggestions = build_suggestions(self.rows, self.codeset, self.results)
            self._populate_table()
            if hasattr(self, "modified_tab"):
                self.modified_tab.refresh_from_parent()
            self.export_btn.setEnabled(bool(self.rows))
            # v0.3.9.5.2.0.1: enable Tools menu actions when rows are loaded
            if hasattr(self, "_point_offset_action"):
                self._point_offset_action.setEnabled(bool(self.rows))
            if hasattr(self, "_elev_offset_action"):
                self._elev_offset_action.setEnabled(bool(self.rows))
            if hasattr(self, "_undo_offset_action"):
                self._undo_offset_action.setEnabled(False)
            # v0.4.2: enable Convert Line Connect Codes action when rows are loaded
            if hasattr(self, "_convert_lc_action"):
                self._convert_lc_action.setEnabled(bool(self.rows))
            self._offset_undo_stack = []  # reset on file open
            if self.settings.get("auto_save_recovery", True):
                recovery.save_session(self.rows, source_path=path, suggestions=self.suggestions)
                self._update_status_bar()  # v0.5.2.3
                if getattr(self, '_recovery_timer', None) is not None:
                    self._recovery_timer.mark_dirty()  # v0.5.3.3 wireup
        except Exception as exc:
            log.exception("Failed to open file: %s", exc)
            self._error_dialog("Open failed", exc)
            self._update_status_bar()  # v0.5.2
            if getattr(self, '_recovery_timer', None) is not None:
                self._recovery_timer.mark_dirty()  # v0.5.3.3 wireup

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

    def _jump_to_row(self, row_index):
        """v0.5.4 raw data caller rewrite: scroll/select by model index."""
        try:
            row_index = int(row_index)
        except Exception:
            return

        if not hasattr(self, "raw_data_model"):
            return

        if row_index < 0 or row_index >= self.raw_data_model.rowCount():
            return

        index = self.raw_data_model.index(row_index, 0)
        self.table.scrollTo(index)
        self.table.selectRow(row_index)

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
        self._update_status_bar()  # v0.5.2.3
        if getattr(self, '_recovery_timer', None) is not None:
            self._recovery_timer.mark_dirty()  # v0.5.3.3 wireup
        # v0.4.2: enable Tools actions on restore as well
        if hasattr(self, "_point_offset_action"):
            self._point_offset_action.setEnabled(bool(self.rows))
        if hasattr(self, "_elev_offset_action"):
            self._elev_offset_action.setEnabled(bool(self.rows))
        if hasattr(self, "_convert_lc_action"):
            self._convert_lc_action.setEnabled(bool(self.rows))
            self._update_status_bar()  # v0.5.2
            if getattr(self, '_recovery_timer', None) is not None:
                self._recovery_timer.mark_dirty()  # v0.5.3.3 wireup

    def closeEvent(self, event):
        # v0.5.3.3 wireup: stop recovery timer before close
        try:
            if getattr(self, '_recovery_timer', None) is not None:
                self._recovery_timer.force_save_now()
                self._recovery_timer.stop()
        except Exception:
            pass
        
        try:
            if self.rows and self.settings.get("auto_save_recovery", True):
                recovery.save_session(self.rows, source_path=self.source_path, suggestions=self.suggestions)
        except Exception as exc:
            log.exception("Failed to save recovery on close: %s", exc)
        super().closeEvent(event)

    def _start_update_check(self, silent):
        if self._update_thread is not None and self._update_thread.isRunning(): return
        # v0.3.9.5.1.5: now uses GitHub Releases API (repo) instead of manifest URL
        repo = self.settings.get("update_repo")
        self._silent_check = silent
        self._update_thread = UpdateCheckThread(__version__, repo, self)
        self._update_thread.result_ready.connect(self._on_update_result)
        self._update_thread.error.connect(self._on_update_error)
        self._update_thread.start()

    def _on_update_result(self, info):
        """v0.3.9.5.1.5: fully-automated install flow via GitHub Releases API."""
        if info is None:
            if not self._silent_check:
                QMessageBox.information(self, "Check for Updates",
                    "Could not reach GitHub. Check your internet connection.")
            return
        if not info.is_newer:
            if not self._silent_check:
                QMessageBox.information(self, "Check for Updates",
                    f"You're up to date (v{__version__}).")
            return
        reply = QMessageBox.question(
            self, "Update Available",
            f"<h3>Rob's Code Wizard v{info.latest_version}</h3>"
            f"<p>You currently have v{__version__}.</p>"
            "<p>Download and install now? This will close the app, install "
            "the new version, and relaunch automatically.</p>",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes: return
        installer = info.find_installer()
        if not installer:
            QMessageBox.warning(self, "Update",
                "No installer found in the latest release.")
            return
        self._start_download_thread(installer)

    def _start_download_thread(self, asset):
        """v0.3.9.5.1.5: kick off background installer download."""
        import tempfile
        from app.ui.update_thread import UpdateDownloadThread
        from app.ui.busy_dialog import BusyDialog
        self._download_dlg = BusyDialog(self, f"Downloading {asset.name}...")
        self._download_dlg.show()
        self._download_thread = UpdateDownloadThread(
            asset, tempfile.gettempdir(), self)
        self._download_thread.progress.connect(self._on_download_progress)
        self._download_thread.finished_with_path.connect(self._on_download_done)
        self._download_thread.error.connect(self._on_download_error)
        self._download_thread.start()

    def _on_download_progress(self, done, total):
        if total and hasattr(self, "_download_dlg") and self._download_dlg:
            pct = int(100 * done / total)
            self._download_dlg.set_text(f"Downloading... {pct}%")

    def _on_download_done(self, path):
        """v0.3.9.5.1.5: launch installer silently, then quit so it can replace files."""
        from PySide6.QtWidgets import QApplication
        from app.services.updater import launch_installer_and_quit
        if hasattr(self, "_download_dlg") and self._download_dlg:
            self._download_dlg.close()
            self._download_dlg = None
        try:
            launch_installer_and_quit(path, silent=True)
            QApplication.quit()
        except Exception as exc:
            log.exception("Launch installer failed: %s", exc)
            self._error_dialog("Update install failed", exc)

    def _on_download_error(self, msg):
        if hasattr(self, "_download_dlg") and self._download_dlg:
            self._download_dlg.close()
            self._download_dlg = None
        self._error_dialog("Download failed", Exception(msg))

    def _on_update_error(self, msg):
        if not self._silent_check:
            QMessageBox.warning(self, "Check for Updates", msg)

    def _show_log_viewer(self):
        dlg = LogViewerDialog(read_recent_log(), self); dlg.exec()

    def _open_log_folder(self):
        log_dir = get_log_dir(); log_dir.mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(log_dir)))
        QMessageBox.information(self, "Report a Problem",
            f"The log folder was opened:\n{log_dir}\n\nAttach '{get_log_path().name}' to your report.")

    def _show_about(self):
        """v0.3.9.5.1.3: custom About dialog with logo from resources/logo.png."""
        import sys as _sys
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
        from PySide6.QtGui import QPixmap
        logo_path = None
        meipass = getattr(_sys, "_MEIPASS", None)
        if meipass:
            p = Path(meipass) / "resources" / "logo.png"
            if p.exists(): logo_path = p
        if logo_path is None:
            p = Path(__file__).resolve().parents[2] / "resources" / "logo.png"
            if p.exists(): logo_path = p
        dlg = QDialog(self)
        dlg.setWindowTitle("About Rob's Code Wizard")
        dlg.setFixedSize(420, 380)
        layout = QVBoxLayout(dlg)
        if logo_path and logo_path.exists():
            logo_label = QLabel()
            pix = QPixmap(str(logo_path))
            if not pix.isNull():
                pix = pix.scaledToHeight(140, Qt.SmoothTransformation)
                logo_label.setPixmap(pix)
                logo_label.setAlignment(Qt.AlignCenter)
                layout.addWidget(logo_label)
        title = QLabel("<h2>Rob's Code Wizard</h2>")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        info = QLabel(
            f"<p>Version <b>{__version__}</b></p>"
            f"<p>Active code set: <b>{self.codeset.name.upper()}</b> "
            f"({len(self.codeset.codes)} codes)</p>"
        )
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)
        btn_row = QHBoxLayout(); btn_row.addStretch(1)
        gh_btn = QPushButton("View on GitHub")
        gh_btn.clicked.connect(
            lambda: QDesktopServices.openUrl(
                QUrl("https://github.com/robert62395-wq/RobsCodeWizard"))
        )
        btn_row.addWidget(gh_btn)
        close_btn = QPushButton("Close"); close_btn.clicked.connect(dlg.accept)
        btn_row.addWidget(close_btn)
        btn_row.addStretch(1)
        layout.addLayout(btn_row)
        dlg.exec()

    def _on_do_not_touch(self):
        """v0.3.9.5.1.6: placeholder for future feature. See TODO below."""
        # TODO: v0.3.9.6+ - implement reserved future capability here
        QMessageBox.warning(
            self, "DO NOT TOUCH",
            "I told you not to touch it!\n\n"
            "Reserved for a future feature. Nothing to see here yet."
        )

    # ------------------------------------------------------------------
    # v0.3.9.5.2.0.1: Point + Elevation offset utilities (Tools menu)
    # ------------------------------------------------------------------
    def _push_offset_undo(self, label):
        """Save a snapshot of self.rows + label before an offset is applied."""
        import copy
        if not hasattr(self, "_offset_undo_stack"):
            self._offset_undo_stack = []
        snapshot = (label, copy.deepcopy(self.rows))
        self._offset_undo_stack.append(snapshot)
        if hasattr(self, "_undo_offset_action"):
            self._undo_offset_action.setEnabled(True)
            self._undo_offset_action.setText(f"Undo Last Offset ({label})")

    def _on_apply_point_offset(self):
        try:
            from PySide6.QtWidgets import QInputDialog, QMessageBox
            from app.services.offsets import apply_point_offset, detect_point_collisions
            if not self.rows:
                return
            offset, ok = QInputDialog.getInt(
                self, "Apply Point Offset",
                "Add this value to every Point number\n(use negative for subtraction):",
                value=1000, minValue=-1000000, maxValue=1000000, step=1,
            )
            if not ok or offset == 0:
                return
            dups = detect_point_collisions(self.rows, offset)
            if dups:
                preview = ", ".join(str(d) for d in dups[:5])
                if len(dups) > 5:
                    preview += f", ... ({len(dups) - 5} more)"
                QMessageBox.warning(
                    self, "Point Offset - Collision",
                    f"Applying offset {offset:+d} would create duplicate Point numbers: "
                    f"{preview}.\n\nAborted; no changes made."
                )
                return
            self._push_offset_undo(f"P {offset:+d}")
            new_rows, applied = apply_point_offset(self.rows, offset)
            self.rows = new_rows
            self.rows = sorted(self.rows, key=_p_sort_key)
            self._populate_table()
            if hasattr(self, "modified_tab"):
                self.modified_tab.refresh_from_parent()
            log.info("Applied point offset %+d to %d rows", offset, applied)
            QMessageBox.information(
                self, "Point Offset Applied",
                f"Point offset of {offset:+d} applied to {applied} rows."
            )
        except Exception as exc:
            log.exception("Point offset failed: %s", exc)
            self._error_dialog("Point Offset failed", exc)

    def _on_apply_elevation_offset(self):
        try:
            from PySide6.QtWidgets import QInputDialog, QMessageBox
            from app.services.offsets import apply_elevation_offset
            if not self.rows:
                return
            offset, ok = QInputDialog.getDouble(
                self, "Apply Elevation Offset",
                "Add this value to every Elevation (Z)\n"
                "(use negative for subtraction; NAVD88 -> IGLD85 is typically negative).\n"
                "Zero-elevation rows are skipped. N and E are never modified.",
                value=0.0, minValue=-1000.0, maxValue=1000.0, decimals=4,
            )
            if not ok or offset == 0.0:
                return
            self._push_offset_undo(f"Z {offset:+.4f}")
            new_rows, applied = apply_elevation_offset(self.rows, offset, skip_zero=True)
            self.rows = new_rows
            self._populate_table()
            if hasattr(self, "modified_tab"):
                self.modified_tab.refresh_from_parent()
            log.info("Applied elevation offset %+.4f to %d rows (zero-elev skipped)", offset, applied)
            QMessageBox.information(
                self, "Elevation Offset Applied",
                f"Elevation offset of {offset:+.4f} applied to {applied} rows.\n"
                "Zero-elevation rows were skipped."
            )
        except Exception as exc:
            log.exception("Elevation offset failed: %s", exc)
            self._error_dialog("Elevation Offset failed", exc)

    def _on_undo_offset(self):
        try:
            if not hasattr(self, "_offset_undo_stack") or not self._offset_undo_stack:
                return
            label, snapshot = self._offset_undo_stack.pop()
            self.rows = snapshot
            self.rows = sorted(self.rows, key=_p_sort_key)
            self._populate_table()
            if hasattr(self, "modified_tab"):
                self.modified_tab.refresh_from_parent()
            log.info("Undid offset: %s", label)
            if hasattr(self, "_undo_offset_action"):
                if self._offset_undo_stack:
                    prev_label = self._offset_undo_stack[-1][0]
                    self._undo_offset_action.setText(f"Undo Last Offset ({prev_label})")
                else:
                    self._undo_offset_action.setEnabled(False)
                    self._undo_offset_action.setText("Undo Last Offset")
        except Exception as exc:
            log.exception("Undo offset failed: %s", exc)
            self._error_dialog("Undo failed", exc)

    # ------------------------------------------------------------------
    # v0.4.2: Convert Line Connect Codes (Tools menu)
    # ------------------------------------------------------------------
    def _on_convert_line_connect(self):
        """Open the Numeric -> Alphabetic line-connect conversion dialog."""
        try:
            if not self.rows:
                return
            # Build {point, description} dicts for the dialog
            dialog_rows = [
                {"point": r.get("P", ""), "description": r.get("D", "")}
                for r in self.rows
            ]
            dlg = ConvertLineConnectDialog(dialog_rows, parent=self)
            if not dlg.exec():
                return
            # Apply: write back to self.rows by index
            updated = dlg.apply_to_rows(dialog_rows)
            changed = 0
            for i, dr in enumerate(updated):
                if i >= len(self.rows):
                    break
                if self.rows[i].get("D", "") != dr["description"]:
                    self.rows[i]["D"] = dr["description"]
                    changed += 1
            # Revalidate + repopulate
            self.results = validate_rows(self.rows, self.codeset)
            self.suggestions = build_suggestions(self.rows, self.codeset, self.results)
            self._populate_table()
            if hasattr(self, "modified_tab"):
                self.modified_tab.refresh_from_parent()
            log.info("Converted line connect codes on %d rows", changed)
            QMessageBox.information(
                self, "Convert Line Connect Codes",
                f"Numeric -> alphabetic conversion applied to {changed} rows.\n"
                "Civil3D can now consume the descriptions directly."
            )
        except Exception as exc:
            log.exception("Convert line connect failed: %s", exc)
            self._error_dialog("Convert Line Connect Codes failed", exc)

    def _handle_zero_elevation_prompt(self):
        """v0.3.9.5.0.9: deprecated. Zero-elev rows are ALWAYS kept and flagged."""
        return

    def _update_status_bar(self):
        """v0.5.2: refresh permanent status bar text."""
        try:
            text = format_permanent_status(
                getattr(self, "codeset", None),
                getattr(self, "source_path", None),
                getattr(self, "rows", None),
                getattr(self, "results", None),
            )
            self.statusBar().showMessage(text)
        except Exception:
            pass

    def _flash_status(self, message, msec=5000):
        """v0.5.2: transient status message."""
        try:
            self.statusBar().showMessage(message, msec)
        except Exception:
            pass

    def _populate_table(self):
        """v0.5.4 raw data caller rewrite: fast model/view populate.

        Old path created thousands of QTableWidgetItems and colored cells one by one.
        New path resets RawDataTableModel once and lets Qt request visible cells on demand.
        """
        import time
        t0 = time.perf_counter()

        if not hasattr(self, "raw_data_model"):
            log.warning("populate skipped: raw_data_model is missing")
            return

        self.raw_data_model.set_data(
            getattr(self, "rows", []),
            getattr(self, "results", []),
            getattr(self, "suggestions", []),
        )

        try:
            if self.raw_data_model.rowCount() > 0:
                self.table.selectRow(0)
        except Exception:
            pass

        elapsed = time.perf_counter() - t0
        log.info(
            "populate: %.3fs (%d rows)",
            elapsed,
            len(getattr(self, "rows", []) or []),
        )

        try:
            self._update_status_bar()
        except Exception:
            pass

        try:
            if getattr(self, "_recovery_timer", None) is not None:
                self._recovery_timer.mark_dirty()
        except Exception:
            pass

    def _apply_row_color(self, i, row=None, result=None):
        """v0.5.4 raw data caller rewrite.

        No-op retained for backward compatibility. Row coloring now happens in
        RawDataTableModel.data(..., Qt.BackgroundRole).
        """
        return

    def _on_context_menu(self, pos):
        """v0.5.4 raw data caller rewrite: context menu for QTableView."""
        if not hasattr(self, "raw_data_model"):
            return

        index = self.table.indexAt(pos)
        if not index.isValid():
            return

        row = index.row()
        suggestion = self.raw_data_model.suggestion(row)

        menu = QMenu(self)

        if suggestion:
            action = QAction("Apply Suggestion", self)
            action.triggered.connect(
                lambda _checked=False, r=row, s=suggestion: self._apply_suggestion(r, s)
            )
            menu.addAction(action)

        jump_action = QAction("Jump to Point", self)
        jump_action.triggered.connect(lambda _checked=False, r=row: self._jump_to_row(r))
        menu.addAction(jump_action)

        menu.exec(self.table.viewport().mapToGlobal(pos))

    def _apply_suggestion(self, row, suggestion=None):
        """v0.5.4 raw data caller rewrite: apply suggestion via RawDataTableModel."""
        try:
            row = int(row)
        except Exception:
            return

        if not hasattr(self, "raw_data_model"):
            return

        if suggestion is None:
            suggestion = self.raw_data_model.suggestion(row)

        if not suggestion:
            return

        self.raw_data_model.apply_suggestion(row, suggestion)

        try:
            if hasattr(self, "modified_tab"):
                self.modified_tab.refresh_from_parent()
        except Exception:
            pass

        try:
            if getattr(self, "_recovery_timer", None) is not None:
                self._recovery_timer.mark_dirty()
        except Exception:
            pass

        try:
            self._update_status_bar()
        except Exception:
            pass
