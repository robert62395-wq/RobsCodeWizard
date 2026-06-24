"""Tests for v0.5.3 corruption-aware translation map loading."""
import json
import pytest
from pathlib import Path
from app.services import translation_map as tm


def _valid_payload():
    return {
        "schema_version": "1.0",
        "map_version": "test",
        "generated": "2026-06-23T00:00:00Z",
        "entries": [
            {
                "id": "vdt-EP->odot-EP",
                "vdt": {"code": "EP", "type": "Point", "description": "Edge of Pavement"},
                "odot": {"code": "EP", "type": "Point", "description": "Edge of Pavement"},
                "confidence": "exact",
                "match_basis": ["description", "type"],
                "score": 1.0,
                "user_override": False,
                "notes": "",
            }
        ],
    }


def test_safe_load_success(tmp_path):
    path = tmp_path / "good.json"
    path.write_text(json.dumps(_valid_payload()), encoding="utf-8")
    data, err = tm.safe_load(path)
    assert err is None
    assert data is not None
    assert len(data["entries"]) == 1


def test_safe_load_missing_file(tmp_path):
    path = tmp_path / "missing.json"
    data, err = tm.safe_load(path)
    assert data is None
    assert "not found" in err.lower()


def test_safe_load_invalid_json(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{ this is not valid json", encoding="utf-8")
    data, err = tm.safe_load(path)
    assert data is None
    assert "JSON parse error" in err


def test_safe_load_missing_required_keys(tmp_path):
    path = tmp_path / "missing_keys.json"
    path.write_text(json.dumps({"schema_version": "1.0"}), encoding="utf-8")
    data, err = tm.safe_load(path)
    assert data is None
    assert "missing keys" in err.lower() or "validation" in err.lower()


def test_save_creates_backup(tmp_path, monkeypatch):
    # Redirect MAP_PATH and BACKUP_PATH to tmp_path
    map_path = tmp_path / "translation_map.json"
    backup_path = tmp_path / "translation_map.backup.json"
    
    monkeypatch.setattr(tm, "MAP_PATH", map_path)
    monkeypatch.setattr(tm, "BACKUP_PATH", backup_path)
    monkeypatch.setattr(tm, "BACKUP_TIMESTAMPED_DIR", tmp_path / "backups")
    
    payload = _valid_payload()
    
    # First save - no existing file, no backup expected
    tm.save(payload, path=map_path)
    assert map_path.exists()
    assert not backup_path.exists()  # no backup on first save
    
    # Modify payload and save again - backup should now appear
    payload["map_version"] = "v2"
    tm.save(payload, path=map_path)
    assert backup_path.exists()
    
    # Backup should contain the OLD version
    with open(backup_path, encoding="utf-8") as f:
        backup_data = json.load(f)
    assert backup_data["map_version"] == "test"


def test_restore_from_backup(tmp_path, monkeypatch):
    map_path = tmp_path / "translation_map.json"
    backup_path = tmp_path / "translation_map.backup.json"
    
    monkeypatch.setattr(tm, "MAP_PATH", map_path)
    monkeypatch.setattr(tm, "BACKUP_PATH", backup_path)
    
    payload = _valid_payload()
    backup_path.write_text(json.dumps(payload), encoding="utf-8")
    
    # Corrupt the main file
    map_path.write_text("corrupt garbage", encoding="utf-8")
    
    assert tm.has_backup(backup=backup_path) is True
    assert tm.restore_from_backup(path=map_path, backup=backup_path) is True
    
    # Should now be loadable
    data, err = tm.safe_load(map_path)
    assert err is None
    assert data["map_version"] == "test"


def test_restore_from_backup_when_no_backup(tmp_path):
    map_path = tmp_path / "translation_map.json"
    backup_path = tmp_path / "missing_backup.json"
    
    assert tm.has_backup(backup=backup_path) is False
    assert tm.restore_from_backup(path=map_path, backup=backup_path) is False