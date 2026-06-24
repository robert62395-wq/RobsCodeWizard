"""Translation map corruption recovery dialog (v0.5.3)."""
from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit,
)


class CorruptionRecoveryDialog(QDialog):
    """Shown when translation_map.json fails to load or validate.
    
    Lets the user choose: restore from backup, reseed from catalog, or cancel.
    """
    
    ACTION_RESTORE = "restore"
    ACTION_RESEED = "reseed"
    ACTION_CANCEL = "cancel"
    
    def __init__(self, error_msg: str, has_backup: bool, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Translation Map Corrupted")
        self.setMinimumWidth(520)
        self._action = self.ACTION_CANCEL
        
        layout = QVBoxLayout(self)
        
        title = QLabel("<h3>Translation map could not be loaded.</h3>")
        title.setTextFormat(Qt.RichText)
        layout.addWidget(title)
        
        explain = QLabel(
            "The file <code>app/data/translation_map.json</code> is corrupted "
            "or invalid. The Translation tab will not work until this is resolved.<br><br>"
            "Choose how to proceed:"
        )
        explain.setWordWrap(True)
        explain.setTextFormat(Qt.RichText)
        layout.addWidget(explain)
        
        layout.addWidget(QLabel("<b>Error details:</b>"))
        details = QTextEdit()
        details.setReadOnly(True)
        details.setMaximumHeight(90)
        details.setPlainText(error_msg)
        layout.addWidget(details)
        
        btn_row = QHBoxLayout()
        
        if has_backup:
            restore_btn = QPushButton("Restore from backup")
            restore_btn.setToolTip(
                "Restore the most recent automatic backup of translation_map.json."
            )
            restore_btn.clicked.connect(self._on_restore)
            btn_row.addWidget(restore_btn)
        
        reseed_btn = QPushButton("Reseed from catalog")
        reseed_btn.setToolTip(
            "Rebuild the translation map from VDT_CODES.xlsx and "
            "ODOT_CODES.xlsx. Discards all manual overrides."
        )
        reseed_btn.clicked.connect(self._on_reseed)
        btn_row.addWidget(reseed_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setToolTip(
            "Close this dialog. The Translation tab will be unavailable until "
            "the file is fixed manually."
        )
        cancel_btn.clicked.connect(self._on_cancel)
        btn_row.addWidget(cancel_btn)
        
        layout.addLayout(btn_row)
    
    def _on_restore(self):
        self._action = self.ACTION_RESTORE
        self.accept()
    
    def _on_reseed(self):
        self._action = self.ACTION_RESEED
        self.accept()
    
    def _on_cancel(self):
        self._action = self.ACTION_CANCEL
        self.reject()
    
    def action(self) -> str:
        """Return the chosen action."""
        return self._action