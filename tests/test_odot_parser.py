import tempfile, pathlib
from app.services.odot_parser import (
    parse_odot, assign_attributes, _split_suffix, _schemas_from_codeset
)
from app.services.catalog_loader import load_catalog


_odot_cs = None
def _odot():
    global _odot_cs
    if _odot_cs is None:
        _odot_cs = load_catalog("odot")
    return _odot_cs


def _write_csv(text):
    p = pathlib.Path(tempfile.mkstemp(suffix=".csv")[1])
    p.write_text(text, encoding="utf-8")
    return p


def test_split_suffix():
    assert _split_suffix("EPA1") == ("EPA", "1")
    assert _split_suffix("EP") == ("EP", "")
    assert _split_suffix("") == ("", "")
    assert _split_suffix("DR123") == ("DR", "123")


def test_parse_simple_row():
    p = _write_csv("17017,593788.144,2073460.779,768.5,EP BL*,Material,Asphalt\n")
    rows = parse_odot(p, _odot())
    assert len(rows) == 1
    row = rows[0]
    assert row["P"] == "17017"
    assert row["D"] == "EP BL*"
    assert len(row["attributes"]) == 1
    assert row["attributes"][0]["code"] == "EP"
    assert row["attributes"][0]["attrs"] == {"Material": "Asphalt"}
    assert row["trailing_attrs"] == {}


def test_parse_no_attributes():
    p = _write_csv("17000,5000,5000,100,ROCK\n")
    rows = parse_odot(p, _odot())
    assert len(rows) == 1
    assert rows[0]["attributes"][0]["code"] == "ROCK"
    assert rows[0]["attributes"][0]["attrs"] == {}


def test_parse_multi_code_distribution():
    p = _write_csv("17035,5000,5000,100,EP DR BL* DR1 BL*,Material,Asphalt,Material,Stone,Material,Stone\n")
    rows = parse_odot(p, _odot())
    assert len(rows) == 1
    attrs = rows[0]["attributes"]
    assert len(attrs) == 3
    by_code = {a["code"]: a for a in attrs}
    assert by_code["EP"]["attrs"] == {"Material": "Asphalt"}
    assert by_code["DR"]["attrs"] == {"Material": "Stone"}
    assert by_code["DR1"]["attrs"] == {"Material": "Stone"}
    assert rows[0]["trailing_attrs"] == {}


def test_parse_schema_perfect_match():
    p = _write_csv(
        "17028,5000,5000,100,"
        "TPP PL PL1 BL* TL BL* TL1 BL*,"
        "Material,Wood,Owner,LMRE,Pole#,6 3 8,"
        "Location,Overhead,Location,Overhead,Location,Overhead,Location,Overhead\n"
    )
    rows = parse_odot(p, _odot())
    assert len(rows) == 1
    attrs = rows[0]["attributes"]
    assert len(attrs) == 5
    by_code = {a["code"]: a for a in attrs}
    assert by_code["TPP"]["attrs"]["Material"] == "Wood"
    assert by_code["TPP"]["attrs"]["Owner"] == "LMRE"
    assert by_code["TPP"]["attrs"]["Pole#"] == "6 3 8"
    for c in ("PL", "PL1", "TL", "TL1"):
        assert by_code[c]["attrs"].get("Location") == "Overhead"


def test_parse_quoted_values():
    csv_text = '2,593876.28,2073685.32,779.18,IPINS,Size,"5/8""",Note,"W/RED ""VERDANTAS REF"" CAP"\n'
    p = _write_csv(csv_text)
    rows = parse_odot(p, _odot())
    assert len(rows) == 1
    attrs = rows[0]["attributes"][0]["attrs"]
    # Size always stored under its file-supplied name
    assert "5/8" in attrs.get("Size", "")
    # The note value may be keyed as "Note" (file label) or "Name" (catalog
    # schema position 1 of IPINS = "Size;Name;Number;Note"). Both are valid;
    # what matters is that the quoted multi-word value parsed correctly.
    note_value = attrs.get("Note") or attrs.get("Name", "")
    assert "VERDANTAS REF" in note_value, f"value not found in attrs: {attrs}"


def test_parse_skips_blank_lines():
    p = _write_csv("\n   \n17000,5000,5000,100,ROCK\n\n")
    rows = parse_odot(p, _odot())
    assert len(rows) == 1
    assert rows[0]["P"] == "17000"


def test_parse_skips_short_rows():
    p = _write_csv("1,2,3\n17000,5000,5000,100,ROCK\n")
    rows = parse_odot(p, _odot())
    assert len(rows) == 1
    assert rows[0]["P"] == "17000"


def test_parse_linework_only_with_attrs():
    p = _write_csv("17090,5000,5000,100,BLD BL*,Use,Commercial\n")
    rows = parse_odot(p, _odot())
    assert len(rows) == 1
    assert rows[0]["attributes"][0]["code"] == "BLD"
    assert rows[0]["attributes"][0]["attrs"] == {"Use": "Commercial"}


def test_assign_attributes_unit():
    schemas = {"EP": ["Material"], "DR": ["Material", "Type"]}
    codes = [(0, "EP"), (1, "DR")]
    pairs = [("Material", "Asphalt"), ("Material", "Stone"), ("Type", "Residential")]
    assignments, trailing = assign_attributes(codes, pairs, schemas)
    assert len(assignments) == 2
    assert assignments[0]["code"] == "EP"
    assert assignments[0]["attrs"] == {"Material": "Asphalt"}
    assert assignments[1]["code"] == "DR"
    assert assignments[1]["attrs"] == {"Material": "Stone", "Type": "Residential"}
    assert trailing == {}


def test_schemas_extracted_from_codeset():
    schemas = _schemas_from_codeset(_odot())
    assert "PP" in schemas
    assert schemas["PP"] == ["Material", "Owner", "Pole#"]
    assert "EP" in schemas
    assert schemas["EP"] == ["Material", "Depth"]


def test_schemas_none_codeset():
    schemas = _schemas_from_codeset(None)
    assert schemas == {}
