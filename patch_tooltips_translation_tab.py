"""v0.5.2.3 Part 2b: tooltips for translation_tab.py."""
import ast
import sys
from pathlib import Path

TT = Path("app/ui/translation_tab.py")
if not TT.exists():
    print(f"[ERROR] {TT} not found.")
    sys.exit(1)

src = TT.read_text(encoding="utf-8")
SENTINEL = "v0.5.2.3 tooltips translation_tab"
if SENTINEL in src:
    print(f"[OK] {TT} already has v0.5.2.3 tooltips.")
    sys.exit(0)

backup = Path("_backup_v0_5_2_3") / TT.name
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(src, encoding="utf-8")
print(f"[OK] Backed up {TT}")

# (anchor_line, tooltip_call_to_inject_right_after)
TOOLTIPS = [
    ('self.target_combo.addItems(["ODOT", "VDT"])',
     'self.target_combo.setToolTip("Dialect to translate loaded rows into (defaults to opposite of Source)")'),
    ('self.translate_btn = QPushButton("Translate Loaded Rows")',
     'self.translate_btn.setToolTip("Rewrite the Description column on all loaded rows. P, N, E, Z never modified.")'),
    ('self.search_box.setPlaceholderText("code or description...")',
     'self.search_box.setToolTip("Filter rows by VDT/ODOT code or description text")'),
    ('self.show_used_only = QCheckBox("Only codes in loaded file")',
     'self.show_used_only.setToolTip("Show only entries for codes that appear in your loaded file")'),
    ('self.show_unmatched = QCheckBox("Unmatched")',
     'self.show_unmatched.setToolTip("Show entries with no automatic match")'),
    ('self.show_bestguess = QCheckBox("Best-guess")',
     'self.show_bestguess.setToolTip("Show entries matched by description similarity")'),
    ('self.show_exact = QCheckBox("Exact")',
     'self.show_exact.setToolTip("Show entries with exact code-equality matches")'),
    ('self.show_manual = QCheckBox("Manual")',
     'self.show_manual.setToolTip("Show entries you have manually overridden")'),
    ('self.bulk_btn = QPushButton("Accept all Best-Guess in view")',
     'self.bulk_btn.setToolTip("Promote every visible best-guess to a manual override in one click")'),
    ('self.save_btn = QPushButton("Save Overrides")',
     'self.save_btn.setToolTip("Persist all manual overrides to translation_map.json")'),
    ('self.export_btn = QPushButton("Export Review CSV")',
     'self.export_btn.setToolTip("Export the visible rows to CSV for offline review")'),
    ('self.reseed_btn = QPushButton("Reseed from Catalog...")',
     'self.reseed_btn.setToolTip("DESTRUCTIVE: Rebuild map from VDT_CODES.xlsx and ODOT_CODES.xlsx. Discards all manual overrides.")'),
]

import re
applied = 0
for anchor, tooltip_call in TOOLTIPS:
    lines = src.split("\n")
    for i, line in enumerate(lines):
        if anchor in line:
            indent = re.match(r"^(\s*)", line).group(1)
            new_line = f"{indent}{tooltip_call}"
            lines.insert(i + 1, new_line)
            src = "\n".join(lines)
            applied += 1
            break

# Add sentinel
if applied > 0:
    src = src.replace(
        '"""Translation Tab v0.5.1.2 - simplified Raw-Data-style layout."""',
        '"""Translation Tab v0.5.1.2 - simplified Raw-Data-style layout.\nv0.5.2.3 tooltips translation_tab applied."""'
    )

# Verify it parses
try:
    ast.parse(src)
    TT.write_text(src, encoding="utf-8")
    print(f"[DONE] Applied {applied}/12 tooltips and saved.")
except SyntaxError as e:
    print(f"[ERROR] Syntax error after patch: {e}")
    print(f"        File NOT saved. Backup is at _backup_v0_5_2_3\\{TT.name}")
    sys.exit(1)