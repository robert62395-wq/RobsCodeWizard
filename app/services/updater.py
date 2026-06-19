"""Auto-update support."""
from __future__ import annotations
import hashlib, json, os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional
from urllib.error import URLError
from urllib.request import Request, urlopen

DEFAULT_MANIFEST_URL = "https://example.invalid/robs-code-wizard/latest.json"
USER_AGENT = "RobsCodeWizard-Updater/0.3.9.3"


@dataclass
class UpdateInfo:
    latest_version: str
    download_url: str
    release_notes: str = ""
    sha256: Optional[str] = None
    is_newer: bool = False


def parse_version(v):
    if not v: return ()
    parts = []
    for token in str(v).strip().split("."):
        token = token.strip()
        if not token: continue
        digits = ""
        for ch in token:
            if ch.isdigit(): digits += ch
            else: break
        if digits == "": break
        parts.append(int(digits))
    return tuple(parts)


def is_newer(latest, current):
    return parse_version(latest) > parse_version(current)


def _default_opener(url, timeout=5.0):
    req = Request(url, headers={"User-Agent": USER_AGENT})
    return urlopen(req, timeout=timeout)


def fetch_manifest(url, timeout=5.0, opener=None):
    op = opener or _default_opener
    resp = op(url, timeout=timeout)
    try: raw = resp.read()
    finally:
        close = getattr(resp, "close", None)
        if close:
            try: close()
            except Exception: pass
    if isinstance(raw, bytes): raw = raw.decode("utf-8")
    return json.loads(raw)


def check_for_update(current_version, manifest_url=DEFAULT_MANIFEST_URL, opener=None):
    try:
        manifest = fetch_manifest(manifest_url, opener=opener)
    except (URLError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[updater] manifest fetch failed: {exc}"); return None
    except Exception as exc:
        print(f"[updater] unexpected manifest error: {exc}"); return None
    try:
        info = UpdateInfo(
            latest_version=str(manifest["latest_version"]),
            download_url=str(manifest["download_url"]),
            release_notes=str(manifest.get("release_notes", "")),
            sha256=manifest.get("sha256"))
    except KeyError as exc:
        print(f"[updater] manifest missing field: {exc}"); return None
    info.is_newer = is_newer(info.latest_version, current_version)
    return info


def download_update(info, dest_dir, opener=None, progress_cb=None, chunk_size=64*1024):
    op = opener or _default_opener
    dest_dir = Path(dest_dir); dest_dir.mkdir(parents=True, exist_ok=True)
    name = os.path.basename(info.download_url) or "update.bin"
    out_path = dest_dir / name
    resp = op(info.download_url, timeout=30.0)
    total = None
    try:
        info_fn = getattr(resp, "info", None)
        if callable(info_fn):
            headers = info_fn()
            length = headers.get("Content-Length") if hasattr(headers, "get") else None
            if length:
                try: total = int(length)
                except (TypeError, ValueError): total = None
    except Exception: total = None
    done = 0
    with out_path.open("wb") as fh:
        while True:
            chunk = resp.read(chunk_size)
            if not chunk: break
            fh.write(chunk); done += len(chunk)
            if progress_cb is not None:
                try: progress_cb(done, total)
                except Exception: pass
    close = getattr(resp, "close", None)
    if close:
        try: close()
        except Exception: pass
    if info.sha256:
        if not verify_sha256(out_path, info.sha256):
            try: out_path.unlink()
            except OSError: pass
            raise ValueError("SHA-256 mismatch on downloaded update")
    return out_path


def verify_sha256(path, expected):
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(64*1024), b""): h.update(chunk)
    return h.hexdigest().lower() == str(expected).lower()


def apply_update_hint(path):
    return (f"Update saved to:\n{path}\n\nTo install:\n"
            "  1. Close Rob\'s Code Wizard.\n"
            "  2. Replace the existing RobsCodeWizard.exe with the downloaded file.\n"
            "  3. Relaunch the application.")
