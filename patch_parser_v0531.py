"""v0.5.3.1 patcher: row-level error recovery for parser.py (PNEZD)."""
import ast
import sys
from pathlib import Path

P = Path("app/services/parser.py")
if not P.exists():
    print(f"[ERROR] {P} not found.")
    sys.exit(1)

src = P.read_text(encoding="utf-8")
SENTINEL = "v0.5.3.1 row error recovery"
if SENTINEL in src:
    print(f"[OK] {P} already patched.")
    sys.exit(0)

backup = Path("_backup_v0_5_3_1") / P.name
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(src, encoding="utf-8")
print(f"[OK] Backed up {P}")

# Replace the entire file content - the original is tiny.
NEW_SRC = '''"""Parse PNEZD survey files (v0.5.3.1 with row-level error recovery)."""
# v0.5.3.1 row error recovery
import csv
from pathlib import Path

from app.services.parse_errors import ParseError, ParseResult

PNEZD_KEYS = ("P", "N", "E", "Z", "D")


def parse_pnezd(path):
    """Legacy API: returns just the rows list."""
    result = parse_pnezd_with_errors(path)
    return result.rows


def parse_pnezd_with_errors(path):
    """v0.5.3.1: returns ParseResult (rows + collected errors)."""
    p = Path(path)
    result = ParseResult()
    with p.open("r", newline="", encoding="utf-8-sig") as f:
        for line_no, raw in enumerate(csv.reader(f), start=1):
            result.total_lines = line_no
            if not raw or all(not str(c).strip() for c in raw):
                continue
            try:
                cells = [str(c).strip() for c in raw[:5]]
                while len(cells) < 5:
                    cells.append("")
                # Basic sanity: P must be non-empty.
                if not cells[0]:
                    result.errors.append(ParseError(
                        line_number=line_no,
                        snippet=",".join(str(c) for c in raw)[:120],
                        reason="Empty Point number (P field)",
                    ))
                    continue
                # Validate N, E, Z are coercible to float if present.
                for i, key in enumerate(("N", "E", "Z"), start=1):
                    if cells[i]:
                        try:
                            float(cells[i])
                        except ValueError:
                            result.errors.append(ParseError(
                                line_number=line_no,
                                snippet=",".join(str(c) for c in raw)[:120],
                                reason=f"Non-numeric {key} value: {cells[i]!r}",
                            ))
                            cells[i] = "0"  # default but flag
                            # Note: still appended row; this is a soft warning, not fatal.
                result.rows.append(dict(zip(PNEZD_KEYS, cells)))
            except Exception as exc:
                result.errors.append(ParseError(
                    line_number=line_no,
                    snippet=",".join(str(c) for c in raw)[:120],
                    reason=f"Unexpected error: {exc}",
                ))
    return result
'''

try:
    ast.parse(NEW_SRC)
except SyntaxError as e:
    print(f"[ERROR] New file would have syntax error: {e}")
    sys.exit(1)

P.write_text(NEW_SRC, encoding="utf-8")
print(f"[DONE] {P} patched (parse_pnezd_with_errors added; parse_pnezd kept as legacy alias).")