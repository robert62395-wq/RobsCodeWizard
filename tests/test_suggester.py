from app.services.suggester import suggest, build_suggestions
from app.services.catalog_loader import load_catalog


def test_suggest_preserves_numeric_suffix():
    assert suggest("EPA1", ["EPA","BDCR","WAFH"]) == "EPA1"


def test_suggest_returns_none_when_no_match():
    assert suggest("QQQQ", ["EPA","BDCR"]) is None


def test_build_suggestions_skips_valid():
    rows = [{"D":"EPA"}, {"D":"EPAX"}]
    results = [{"valid":True,"issues":[]}, {"valid":False,"issues":[]}]
    out = build_suggestions(rows, ["EPA","BDCR","WAFH"], results)
    assert out[0] == "" and out[1] == "EPA"


def test_passes_through_linework_commands():
    vdt = load_catalog("vdt")
    rows = [{"D":"EPA B EPAX"}]
    results = [{"valid":False,"issues":[]}]
    out = build_suggestions(rows, vdt, results)
    tokens = out[0].split()
    assert "B" in tokens
    assert "EPA" in tokens
    assert "EPAX" not in tokens
