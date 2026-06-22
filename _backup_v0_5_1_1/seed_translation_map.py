"""Auto-seed translation_map.json from VDT_CODES.xlsx and ODOT_CODES.xlsx."""
import argparse
from datetime import datetime, timezone

from rapidfuzz import fuzz

from app.catalogs import vdt_codes, odot_codes
from app.services import translation_map as tm

EXACT_THRESHOLD = 95
BEST_GUESS_THRESHOLD = 70
MAP_VERSION = "0.4.1"


def score_pair(vdt_row: dict, odot_row: dict) -> int:
    if vdt_row["type"] != odot_row["type"]:
        return 0  # hard filter on point style
    return fuzz.token_set_ratio(vdt_row["description"], odot_row["description"])


def best_odot_match(vdt_row: dict, odot_rows: list) -> tuple:
    best, best_score = None, 0
    for o in odot_rows:
        s = score_pair(vdt_row, o)
        if s > best_score:
            best, best_score = o, s
    return best, best_score


def build_entry(vdt_row, odot_row, score) -> dict:
    if score >= EXACT_THRESHOLD:
        confidence = "exact"
    elif score >= BEST_GUESS_THRESHOLD:
        confidence = "best-guess"
    else:
        confidence = "unmatched"
        odot_row = None
    return {
        "id": f"vdt-{vdt_row['code']}->odot-{odot_row['code'] if odot_row else 'NONE'}",
        "vdt": vdt_row,
        "odot": odot_row,
        "confidence": confidence,
        "match_basis": ["description", "type"] if odot_row else [],
        "score": round(score / 100, 2),
        "user_override": False,
        "notes": "",
    }


def seed(force: bool = False) -> dict:
    if tm.MAP_PATH.exists() and not force:
        existing = tm.load()
        if existing["entries"]:
            print(f"[OK] Existing map preserved ({len(existing['entries'])} entries).")
            print("     Run reseed_translation_map.bat to force regen.")
            return existing

    vdt_rows = vdt_codes.load_all()
    odot_rows = odot_codes.load_all()

    entries = []
    matched_odot_codes = set()

    # Forward pass: VDT -> ODOT
    for v in vdt_rows:
        candidates = [o for o in odot_rows if o["type"] == v["type"]]
        match, score = best_odot_match(v, candidates)
        entry = build_entry(v, match, score)
        entries.append(entry)
        if match and score >= BEST_GUESS_THRESHOLD:
            matched_odot_codes.add(match["code"])

    # Reverse pass: orphaned ODOT codes
    for o in odot_rows:
        if o["code"] not in matched_odot_codes:
            entries.append({
                "id": f"vdt-NONE->odot-{o['code']}",
                "vdt": None,
                "odot": o,
                "confidence": "unmatched",
                "match_basis": [],
                "score": 0.0,
                "user_override": False,
                "notes": "No VDT counterpart auto-detected.",
            })

    entries.sort(key=lambda e: (e["vdt"]["code"] if e["vdt"] else "zzz",
                                e["odot"]["code"] if e["odot"] else "zzz"))

    data = {
        "schema_version": tm.SCHEMA_VERSION,
        "map_version": MAP_VERSION,
        "generated": datetime.now(timezone.utc).isoformat(),
        "entries": entries,
    }
    tm.save(data)

    summary = {"total": len(entries),
               "exact": sum(1 for e in entries if e["confidence"] == "exact"),
               "best_guess": sum(1 for e in entries if e["confidence"] == "best-guess"),
               "unmatched": sum(1 for e in entries if e["confidence"] == "unmatched")}
    print(f"[OK] Seeded {summary['total']} entries: "
          f"{summary['exact']} exact / {summary['best_guess']} best-guess / "
          f"{summary['unmatched']} unmatched.")
    return data


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--force", action="store_true", help="Overwrite existing map")
    args = p.parse_args()
    seed(force=args.force)
