"""v0.5.2.3 Part 2c: ? help icons for translation_tab.py."""
import ast
import re
import sys
from pathlib import Path

TT = Path("app/ui/translation_tab.py")
if not TT.exists():
    print(f"[ERROR] {TT} not found.")
    sys.exit(1)

src = TT.read_text(encoding="utf-8")
SENTINEL = "v0.5.2.3 help icons translation_tab"
if SENTINEL in src:
    print(f"[OK] {TT} already has v0.5.2.3 help icons.")
    sys.exit(0)

backup = Path("_backup_v0_5_2_3") / TT.name
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(src, encoding="utf-8")
print(f"[OK] Backed up {TT}")

# Step 1 — ensure HelpIcon is imported
if "from app.ui.help_icon import HelpIcon" not in src:
    # Add after the existing PySide6 imports
    src = src.replace(
        "from app.services.match_basis_descriptor import short_label",
        "from app.services.match_basis_descriptor import short_label\nfrom app.ui.help_icon import HelpIcon"
    )
    print("[OK] Added HelpIcon import")

# Step 2 — anchors for layout-based icon insertion.
# Each entry is: (anchor_line, layout_var, addWidget_call_to_inject_after)
# The HelpIcon is added to the same layout that the anchor's widget was added to.
INSERTIONS = [
    # After: bar.addWidget(self.target_combo) → add Help icon
    ('bar.addWidget(self.target_combo)',
     'bar.addWidget(HelpIcon("translate_source_target"))'),
    # After: bar.addWidget(self.translate_btn) → add Help icon
    ('bar.addWidget(self.translate_btn)',
     'bar.addWidget(HelpIcon("translate_button"))'),
    # After: filt.addWidget(cb) loop appends self.show_used_only first → add icon to filt right after the loop block
    # Note: this anchor matches the line where the loop ends
    ('filt.addStretch(1)',
     'filt.insertWidget(filt.count() - 1, HelpIcon("translate_filter_used"))'),
    # After: action.addWidget(self.bulk_btn) → add Help icon
    ('action.addWidget(self.bulk_btn)',
     'action.addWidget(HelpIcon("translate_bulk_accept"))'),
    # After: action.addWidget(self.reseed_btn) → add Help icon
    ('action.addWidget(self.reseed_btn)',
     'action.addWidget(HelpIcon("translate_reseed"))'),
]

applied = 0
for anchor, injection in INSERTIONS:
    lines = src.split("\n")
    found = False
    for i, line in enumerate(lines):
        if anchor in line and "HelpIcon" not in line:
            indent = re.match(r"^(\s*)", line).group(1)
            new_line = f"{indent}{injection}"
            lines.insert(i + 1, new_line)
            src = "\n".join(lines)
            applied += 1
            found = True
            break
    if not found:
        print(f"[WARN] anchor not found: {anchor[:60]}")

# Step 3 — add sentinel
src = src.replace(
    '"""Translation Tab v0.5.1.2 - simplified Raw-Data-style layout.',
    '"""Translation Tab v0.5.1.2 - simplified Raw-Data-style layout.\nv0.5.2.3 help icons translation_tab applied.'
)

# Step 4 — verify it parses, then save
try:
    ast.parse(src)
    TT.write_text(src, encoding="utf-8")
    print(f"\n[DONE] Applied {applied}/5 help icons and saved.")
except SyntaxError as e:
    print(f"[ERROR] Syntax error after patch: {e}")
    print(f"        File NOT saved. Backup is at _backup_v0_5_2_3\\{TT.name}")
    sys.exit(1)