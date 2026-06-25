"""v0.5.5 verification: Translation tab model/view migration sanity check."""

import ast
import sys
from pathlib import Path

TT = Path("app/ui/translation_tab.py")
MODEL = Path("app/ui/translation_model.py")

errors = []

if not TT.exists():
    errors.append("Missing app/ui/translation_tab.py")

if not MODEL.exists():
    errors.append("Missing app/ui/translation_model.py")

if errors:
    for e in errors:
        print("[ERROR]", e)
    sys.exit(1)

src = TT.read_text(encoding="utf-8")
model_src = MODEL.read_text(encoding="utf-8")

# Syntax checks
try:
    ast.parse(src)
    print("[OK] translation_tab.py syntax")
except SyntaxError as e:
    print("[ERROR] translation_tab.py syntax:", e)
    sys.exit(1)

try:
    ast.parse(model_src)
    print("[OK] translation_model.py syntax")
except SyntaxError as e:
    print("[ERROR] translation_model.py syntax:", e)
    sys.exit(1)

# Required imports / architecture checks
checks = [
    ("QTableView import", "QTableView" in src),
    ("TranslationTableModel import", "TranslationTableModel" in src),
    ("QTableView table creation", "self.table = QTableView" in src),
    ("model set on table", "self.table.setModel" in src),
    ("old QTableWidget creation removed", "self.table = QTableWidget" not in src),
    ("broken self.banner reference removed", "self.banner" not in src),
    ("forced white table style removed", "background-color: #FFFFFF" not in src),
    ("TranslationTableModel class exists", "class TranslationTableModel" in model_src),
]

failed = False
for label, ok in checks:
    if ok:
        print(f"[OK] {label}")
    else:
        print(f"[FAIL] {label}")
        failed = True

if failed:
    print("\n[RESULT] v0.5.5 translation migration has issues.")
    sys.exit(1)

print("\n[RESULT] v0.5.5 translation migration structure looks good.")
print("Next: run pytest and smoke-test the Translation tab.")