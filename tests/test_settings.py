from app.services import settings as s


def test_default_keys(monkeypatch, tmp_path):
    monkeypatch.setattr(s, "_settings_path", lambda: tmp_path / "s.json")
    data = s.load_settings()
    for k in ("update_repo","check_on_startup","auto_save_recovery","active_codeset"):
        assert k in data


def test_roundtrip(monkeypatch, tmp_path):
    monkeypatch.setattr(s, "_settings_path", lambda: tmp_path / "s.json")
    s.set_setting("active_codeset", "odot")
    assert s.get_setting("active_codeset") == "odot"
