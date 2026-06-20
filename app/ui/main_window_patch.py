"""Phase 2 integration notes for app/main_window.py.

This file is documentation, not executable code. It is shipped in the overlay
so you have the exact snippets to paste, but apply_phase_2.bat will NOT modify
your main_window.py automatically. Lesson learned from the v0.4.1.1 hotfix:
phase overlays never overwrite existing top-level files unless the change is
intentional and called out in the changelog.

------------------------------------------------------------------------
1) Insert Translation Tab between "Raw Data" (index 0) and "Linework Fix"
   (currently index 1):

    from app.ui.translation_tab import TranslationTab

    # ... inside MainWindow.__init__, AFTER the tab widget is created and
    # AFTER the Raw Data tab has been added but BEFORE Linework Fix is added:
    self.translation_tab = TranslationTab(self)
    self.tab_widget.insertTab(1, self.translation_tab, "Translation")

   If your tabs are all added in a fixed sequence, just insert the new line
   between the Raw Data addTab() and the Linework Fix addTab() calls.

------------------------------------------------------------------------
2) Add Tools menu item (top-level Tools menu, per Phase 2 decision):

    from app.ui.convert_line_connect_dialog import ConvertLineConnectDialog

    # ... inside MainWindow._build_menus (or wherever menus are constructed):
    tools_menu = self.menuBar().addMenu("Tools")
    convert_lc_action = tools_menu.addAction("Convert Line Connect Codes...")
    convert_lc_action.triggered.connect(self._open_convert_line_connect_dialog)

   If a Tools menu already exists, reuse the reference instead of addMenu().

------------------------------------------------------------------------
3) Add the handler method on MainWindow:

    def _open_convert_line_connect_dialog(self):
        rows = self._get_current_rows()  # however your app exposes the active table rows
        selected = self._get_selected_rows() if hasattr(self, "_get_selected_rows") else None
        dlg = ConvertLineConnectDialog(rows, selected_rows=selected, parent=self)
        if dlg.exec():
            updated = dlg.apply_to_rows(rows)
            self._update_rows(updated)
            self._revalidate()

   Replace `_get_current_rows`, `_get_selected_rows`, `_update_rows`, and
   `_revalidate` with whatever your MainWindow already exposes. Each row dict
   must contain at least {"point": ..., "description": ...}.
