from app.services import recovery


def test_save_load(monkeypatch, tmp_path):
    monkeypatch.setattr(recovery, "get_recovery_path", lambda: tmp_path / "r.json")
    rows = [{"P":"1","N":"1","E":"1","Z":"100","D":"EPA"}]
    recovery.save_session(rows, source_path="/tmp/x.csv", suggestions=[""])
    assert recovery.load_session()["rows"] == rows


def test_clear(monkeypatch, tmp_path):
    p = tmp_path / "r.json"
    monkeypatch.setattr(recovery, "get_recovery_path", lambda: p)
    recovery.save_session([{"P":"1"}]); assert p.exists()
    recovery.clear_session(); assert not p.exists()


def test_no_session(monkeypatch, tmp_path):
    monkeypatch.setattr(recovery, "get_recovery_path", lambda: tmp_path / "nope.json")
    assert recovery.has_session() is False
