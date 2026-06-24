"""Inspect main_window.py for Raw Data table methods before v0.5.4 Step 3."""
import ast
from pathlib import Path

P = Path("app/ui/main_window.py")
src = P.read_text(encoding="utf-8")

print("=== Method names in main_window.py ===")
tree = ast.parse(src)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        print(f"{node.lineno:4d}: {node.name}")

print()
print("=== Lines containing old QTableWidget-style APIs ===")
needles = [
    "setRowCount",
    "insertRow",
    "setItem",
    "QTableWidgetItem",
    "self.table.item",
    "scrollToItem",
    "_apply_row_color",
    "_populate_table",
    "_apply_suggestion",
    "_on_context_menu",
    "_jump_to_row",
]
for i, line in enumerate(src.splitlines(), start=1):
    if any(n in line for n in needles):
        print(f"{i:4d}: {line}")