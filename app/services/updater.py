"""Auto-update via GitHub Releases API (v0.3.9.5.1.5.1)."""
from __future__ import annotations
import json, os, subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen

DEFAULT_REPO = "robert62395-wq/RobsCodeWizard"
GITHUB_API_BASE = "https://api.github.com/repos"
USER_AGENT = "RobsCodeWizard-Updater/0.3.9.5.1.5.1"
DEFAULT_MANIFEST_URL = ""  # back-compat import shim


@dataclass
class ReleaseAsset:
    name: str
    download_url: str
    size: int = 0


@dataclass
class UpdateInfo:
    latest_version: str
    tag_name: str = ""
    release_notes: str = ""
    html_url: str = ""
    assets: List[ReleaseAsset] = field(default_factory=list)
    is_newer: bool = False

    def find_installer(self):
        for a in self.assets:
            if a.name.lower().endswith("_setup.exe"):
                return a
        return None

    def find_portable_exe(self):
        for a in self.assets:
            n = a.name.lower()
            if n.endswith(".exe") and "setup" not in n:
                return a
        return None


def parse_version(v):
    if not v:
        return ()
    s = str(v).strip().lstrip("vV")
    parts = []
    for token in s.split("."):
        token = token.strip()
        if not token:
            continue
        digits = ""
        for ch in token:
            if ch.isdigit():
                digits += ch
            else:
                break
        if not digits:
            break
        parts.append(int(digits))
    return tuple(parts)


def is_newer(latest, current):
    return parse_version(latest) > parse_version(current)


def _default_opener(url, timeout=10.0):
    req = Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/vnd.github+json",
    })
    return urlopen(req, timeout=timeout)


def _read_json(resp):
    try:
        raw = resp.read()
    finally:
        close = getattr(resp, "close", None)
        if close:
            try:
                close()
            except Exception:
                pass
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")
    return json.loads(raw)


def fetch_latest_release(repo=DEFAULT_REPO, timeout=10.0, opener=None):
    """GET /repos/{repo}/releases/latest. Raises HTTPError(404) when no published release exists."""
    op = opener or _default_opener
    url = f"{GITHUB_API_BASE}/{repo}/releases/latest"
    resp = op(url, timeout=timeout)
    return _read_json(resp)


def fetch_releases_list(repo=DEFAULT_REPO, timeout=10.0, opener=None):
    """GET /repos/{repo}/releases (list). Used as fallback when /latest is 404."""
    op = opener or _default_opener
    url = f"{GITHUB_API_BASE}/{repo}/releases"
    resp = op(url, timeout=timeout)
    return _read_json(resp)


def _build_info_from_release(rel):
    """Build an UpdateInfo from a release dict (is_newer left False; caller sets it)."""
    tag = str(rel.get("tag_name", ""))
    latest = tag.lstrip("vV") if tag else ""
    assets = []
    for a in rel.get("assets", []):
        assets.append(ReleaseAsset(
            name=str(a.get("name", "")),
            download_url=str(a.get("browser_download_url", "")),
            size=int(a.get("size", 0)) if a.get("size") else 0,
        ))
    return UpdateInfo(
        latest_version=latest,
        tag_name=tag,
        release_notes=str(rel.get("body", "")),
        html_url=str(rel.get("html_url", "")),
        assets=assets,
    )


def check_for_update(current_version, repo=DEFAULT_REPO, opener=None):
    """Returns UpdateInfo or None.

    Tries /releases/latest first. If that returns 404 (no published
    non-prerelease, or no releases at all), falls back to listing
    /releases and using the first non-draft entry.
    """
    repo = repo or DEFAULT_REPO
    rel = None
    try:
        rel = fetch_latest_release(repo, opener=opener)
    except HTTPError as exc:
        if exc.code == 404:
            # v0.3.9.5.1.5.1: fall back to /releases list
            try:
                lst = fetch_releases_list(repo, opener=opener)
            except (URLError, OSError, ValueError, json.JSONDecodeError) as exc2:
                print(f"[updater] fallback list failed: {exc2}")
                return None
            except Exception as exc2:
                print(f"[updater] unexpected fallback error: {exc2}")
                return None
            if not isinstance(lst, list) or len(lst) == 0:
                print("[updater] no releases on GitHub yet")
                return None
            rel = None
            for entry in lst:
                if isinstance(entry, dict) and not entry.get("draft", False):
                    rel = entry
                    break
            if rel is None:
                print("[updater] only draft releases on GitHub")
                return None
        else:
            print(f"[updater] failed to fetch latest release: {exc}")
            return None
    except (URLError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[updater] failed to fetch latest release: {exc}")
        return None
    except Exception as exc:
        print(f"[updater] unexpected error: {exc}")
        return None
    try:
        info = _build_info_from_release(rel)
    except (TypeError, ValueError, AttributeError) as exc:
        print(f"[updater] malformed release JSON: {exc}")
        return None
    info.is_newer = is_newer(info.latest_version, current_version)
    return info


def download_asset(asset, dest_dir, opener=None, progress_cb=None, chunk_size=64*1024):
    op = opener or _default_opener
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    out_path = dest_dir / asset.name
    resp = op(asset.download_url, timeout=60.0)
    total = asset.size or None
    done = 0
    with out_path.open("wb") as fh:
        while True:
            chunk = resp.read(chunk_size)
            if not chunk:
                break
            fh.write(chunk)
            done += len(chunk)
            if progress_cb is not None:
                try:
                    progress_cb(done, total)
                except Exception:
                    pass
    close = getattr(resp, "close", None)
    if close:
        try:
            close()
        except Exception:
            pass
    if asset.size and out_path.stat().st_size != asset.size:
        try:
            out_path.unlink()
        except OSError:
            pass
        raise ValueError(
            f"Download size mismatch: expected {asset.size}, got {out_path.stat().st_size}"
        )
    return out_path


def launch_installer_and_quit(installer_path, silent=True):
    """Spawn Inno Setup installer and detach so it survives our exit."""
    flags = []
    if silent:
        flags.extend(["/VERYSILENT", "/SUPPRESSMSGBOXES"])
    else:
        flags.append("/SILENT")
    flags.extend(["/CLOSEAPPLICATIONS", "/RESTARTAPPLICATIONS", "/NORESTART"])
    creationflags = 0
    if os.name == "nt":
        # CREATE_NEW_PROCESS_GROUP | DETACHED_PROCESS
        creationflags = 0x00000200 | 0x00000008
    return subprocess.Popen(
        [str(installer_path)] + flags,
        creationflags=creationflags,
        close_fds=True,
    )


def download_update(info, dest_dir, opener=None, progress_cb=None, chunk_size=64*1024):
    """Legacy entry. Downloads installer (preferred) or portable EXE."""
    asset = info.find_installer() or info.find_portable_exe()
    if not asset:
        raise ValueError("No suitable asset found in release")
    return download_asset(asset, dest_dir, opener=opener,
                          progress_cb=progress_cb, chunk_size=chunk_size)


def apply_update_hint(path):
    return (f"Update saved to:\n{path}\n\n"
            "To install: close Rob's Code Wizard and run the installer.")

