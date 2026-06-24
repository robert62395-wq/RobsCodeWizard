"""v0.5.2.3: 'Under Construction' splash overlay for Translation tab."""
import ast
import re
import sys
from pathlib import Path

TT = Path("app/ui/translation_tab.py")
if not TT.exists():
    print(f"[ERROR] {TT} not found.")
    sys.exit(1)

src = TT.read_text(encoding="utf-8")
SENTINEL = "v0.5.2.3 under construction banner"
if SENTINEL in src:
    print(f"[OK] {TT} already has under-construction banner.")
    sys.exit(0)

backup = Path("_backup_v0_5_2_3") / TT.name
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(src, encoding="utf-8")
print(f"[OK] Backed up {TT}")

# Step 1 — add QFrame and settings imports if not present
if "QFrame" not in src:
    src = src.replace(
        "QHeaderView, QCheckBox, QDialog, QGridLayout, QTextEdit,",
        "QHeaderView, QCheckBox, QDialog, QGridLayout, QTextEdit, QFrame,"
    )
    print("[OK] Added QFrame import")

if "from app.services.settings" not in src:
    src = src.replace(
        "from app.services.match_basis_descriptor import short_label",
        "from app.services.match_basis_descriptor import short_label\n"
        "from app.services.settings import load_settings, set_setting"
    )
    print("[OK] Added settings import")

# Step 2 — inject _build_under_construction_banner method right before _build_ui
BANNER_METHOD = '''
    def _build_under_construction_banner(self):
        """v0.5.2.3 — warns users this tab is being rebuilt."""
        settings = load_settings()
        if settings.get("translation_under_construction_hidden", False):
            self._uc_banner = None
            return None

        frame = QFrame()
        frame.setStyleSheet(
            "QFrame { background-color: #FFF3CD; border: 2px solid #FFB300;"
            " border-radius: 4px; padding: 8px; }"
        )
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(10, 6, 10, 6)

        icon_lbl = QLabel("🚧")
        icon_lbl.setStyleSheet("font-size: 20px; background: transparent; border: none;")
        layout.addWidget(icon_lbl)

        msg_lbl = QLabel(
            "<b>Under construction.</b> The Translation tab is being rebuilt. "
            "The automatic matching algorithm produces low-quality suggestions today. "
            "Manual review of every entry is recommended before saving overrides."
        )
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(msg_lbl, 1)

        dismiss_btn = QPushButton("Dismiss for this session")
        dismiss_btn.setStyleSheet("padding: 4px 10px;")
        dismiss_btn.clicked.connect(lambda: frame.setVisible(False))
        layout.addWidget(dismiss_btn)

        hide_forever_btn = QPushButton("Don't show again")
        hide_forever_btn.setStyleSheet("padding: 4px 10px;")
        def _hide_forever():
            set_setting("translation_under_construction_hidden", True)
            frame.setVisible(False)
        hide_forever_btn.clicked.connect(_hide_forever)
        layout.addWidget(hide_forever_btn)

        self._uc_banner = frame
        return frame

    '''

ANCHOR_BEFORE_BUILD_UI = "    def _build_ui(self):"
if ANCHOR_BEFORE_BUILD_UI in src:
    src = src.replace(ANCHOR_BEFORE_BUILD_UI, BANNER_METHOD + ANCHOR_BEFORE_BUILD_UI, 1)
    print("[OK] Inserted _build_under_construction_banner method")
else:
    print("[ERROR] Could not find _build_ui anchor")
    sys.exit(1)

# Step 3 — wire banner into _build_ui at the very top (right after root = QVBoxLayout)
ROOT_LAYOUT_LINE = "root = QVBoxLayout(self)"
BANNER_INJECT = (
    "root = QVBoxLayout(self)\n"
    "        # v0.5.2.3 under construction banner\n"
    "        uc_banner = self._build_under_construction_banner()\n"
    "        if uc_banner is not None:\n"
    "            root.addWidget(uc_banner)"
)
if ROOT_LAYOUT_LINE in src:
    src = src.replace(ROOT_LAYOUT_LINE, BANNER_INJECT, 1)
    print("[OK] Wired banner into _build_ui")
else:
    print("[ERROR] Could not find root layout anchor")
    sys.exit(1)

# Step 4 — verify it parses, then save
try:
    ast.parse(src)
    TT.write_text(src, encoding="utf-8")
    print("\n[DONE] Under-construction banner added.")
except SyntaxError as e:
    print(f"[ERROR] Syntax error after patch: {e}")
    print(f"        File NOT saved. Backup is at _backup_v0_5_2_3\\{TT.name}")
    sys.exit(1)