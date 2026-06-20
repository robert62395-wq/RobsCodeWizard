"""Per-user settings (JSON) (v0.3.9.5.1.5)."""
from __future__ import annotations
import json
from pathlib import Path

DEFAULT_UPDATE_REPO = "robert62395-wq/RobsCodeWizard"


def _settings_path():
    return Path.home() / ".robs_code_wizard" / "settings.json"


DEFAULTS = {
    "update_repo": DEFAULT_UPDATE_REPO,
    "check_on_startup": True,
    "auto_save_recovery": True,
    "active_codeset": "vdt",
}


def load_settings():
    p = _settings_path()
    if not p.exists():
        return dict(DEFAULTS)
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return dict(DEFAULTS)
    merged = dict(DEFAULTS)
    if isinstance(data, dict):
        # v0.3.9.5.1.5: migration - drop deprecated manifest_url key
        data.pop("manifest_url", None)
        merged.update(data)
    return merged


def save_settings(data):
    p = _settings_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")


def get_setting(key, default=None):
    return load_settings().get(key, default)


def set_setting(key, value):
    data = load_settings()
    data[key] = value
    save_settings(data)

