"""v0.5.2.3: 'Under Construction' splash overlay for Translation tab (v2 - safer)."""
import ast
import re
import sys
from pathlib import Path

TT = Path("app/ui/translation_tab.py")
src = TT.read_text(encoding="utf-8")

SENTINEL = "v0.5.2.3 under construction banner"
if SENTINEL in src:
    print(f"[OK] Already patched.")
    sys.exit(0)

backup = Path("_backup_v0_5_2_3") / TT.name
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(src, encoding="utf-8")
print("[OK] Backed up file")

# Step 1 — imports
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

# Step 2 — locate the start of the TranslationTab class _build_ui method.
# Insert the banner method INSIDE the class, right before _build_ui's `def`.
# Approach: find the line "    def _build_ui(self):" within class TranslationTab,
# get the indentation, and prepend our method with matching indentation.
lines = src.split("\n")
build_ui_idx = None
for i, line in enumerate(lines):
    if line.strip() == "def _build_ui(self):":
        # Make sure we're inside TranslationTab class (not EntryEditDialog)
        # by checking context above
        for j in range(i, 0, -1):
            if lines[j].startswith("class TranslationTab"):
                build_ui_idx = i
                break
            elif lines[j].startswith("class "):
                # Different class - skip
                break
        if build_ui_idx == i:
            break

if build_ui_idx is None:
    print("[ERROR] Could not find _build_ui in TranslationTab class")
    sys.exit(1)

indent = "    "  # methods inside class are indented 4 spaces

banner_method = f'''{indent}def _build_under_construction_banner(self):
{indent}    """v0.5.2.3 — warns users this tab is being rebuilt."""
{indent}    settings = load_settings()
{indent}    if settings.get("translation_under_construction_hidden", False):
{indent}        return None

{indent}    frame = QFrame()
{indent}    frame.setStyleSheet(
{indent}        "QFrame {{ background-color: #FFF3CD; border: 2px solid #FFB300;"
{indent}        " border-radius: 4px; padding: 8px; }}"
{indent}    )
{indent}    layout = QHBoxLayout(frame)
{indent}    layout.setContentsMargins(10, 6, 10, 6)

{indent}    icon_lbl = QLabel("[!]")
{indent}    icon_lbl.setStyleSheet("font-size: 18px; font-weight: bold; background: transparent; border: none; color: #d35400;")
{indent}    layout.addWidget(icon_lbl)

{indent}    msg_lbl = QLabel(
{indent}        "<b>Under construction.</b> The Translation tab is being rebuilt. "
{indent}        "The automatic matching algorithm produces low-quality suggestions today. "
{indent}        "Manual review of every entry is recommended before saving overrides."
{indent}    )
{indent}    msg_lbl.setWordWrap(True)
{indent}    msg_lbl.setStyleSheet("background: transparent; border: none;")
{indent}    layout.addWidget(msg_lbl, 1)

{indent}    dismiss_btn = QPushButton("Dismiss for this session")
{indent}    dismiss_btn.setStyleSheet("padding: 4px 10px;")
{indent}    dismiss_btn.clicked.connect(lambda: frame.setVisible(False))
{indent}    layout.addWidget(dismiss_btn)

{indent}    hide_forever_btn = QPushButton("Don't show again")
{indent}    hide_forever_btn.setStyleSheet("padding: 4px 10px;")
{indent}    def _hide_forever():
{indent}        set_setting("translation_under_construction_hidden", True)
{indent}        frame.setVisible(False)
{indent}    hide_forever_btn.clicked.connect(_hide_forever)
{indent}    layout.addWidget(hide_forever_btn)

{indent}    return frame
'''

# Insert the banner method right before _build_ui
lines.insert(build_ui_idx, banner_method)
src = "\n".join(lines)
print("[OK] Inserted _build_under_construction_banner method")

# Step 3 — wire the banner into _build_ui
ROOT = "        root = QVBoxLayout(self)"
WIRED = (
    "        root = QVBoxLayout(self)\n"
    "        # v0.5.2.3 under construction banner\n"
    "        _uc = self._build_under_construction_banner()\n"
    "        if _uc is not None:\n"
    "            root.addWidget(_uc)"
)
if ROOT in src and "_build_under_construction_banner()" not in src.split(ROOT, 1)[1][:200]:
    src = src.replace(ROOT, WIRED, 1)
    print("[OK] Wired banner into _build_ui")
else:
    print("[WARN] Could not wire banner (or already wired)")

# Add sentinel as a comment
sentinel_comment = f"# {SENTINEL}\n"
if sentinel_comment not in src:
    src = sentinel_comment + src

# Verify and save
try:
    ast.parse(src)
    TT.write_text(src, encoding="utf-8")
    print("\n[DONE] Banner added and verified.")
except SyntaxError as e:
    print(f"[ERROR] Syntax error: {e}")
    print(f"        File NOT saved. Restore from backup if needed.")
    sys.exit(1)