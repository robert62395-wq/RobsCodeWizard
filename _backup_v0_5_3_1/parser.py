"""Parse PNEZD survey files."""
import csv
from pathlib import Path
PNEZD_KEYS = ("P", "N", "E", "Z", "D")


def parse_pnezd(path):
    p = Path(path)
    rows = []
    with p.open("r", newline="", encoding="utf-8-sig") as f:
        for raw in csv.reader(f):
            if not raw or all(not str(c).strip() for c in raw):
                continue
            cells = [c.strip() for c in raw[:5]]
            while len(cells) < 5:
                cells.append("")
            rows.append(dict(zip(PNEZD_KEYS, cells)))
    return rows
