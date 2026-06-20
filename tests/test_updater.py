"""Tests for the GitHub Releases updater (v0.3.9.5.1.5.1)."""
import json
import pytest
from urllib.error import HTTPError, URLError

from app.services.updater import (
    parse_version, is_newer,
    ReleaseAsset, UpdateInfo,
    check_for_update,
)


def test_parse_version_strips_v_prefix():
    assert parse_version("v0.3.9.5.1") == (0, 3, 9, 5, 1)
    assert parse_version("V1.2.3") == (1, 2, 3)


def test_parse_version_handles_plain():
    assert parse_version("0.3.9.5.0") == (0, 3, 9, 5, 0)
    assert parse_version("") == ()


def test_is_newer_with_v_prefix():
    assert is_newer("v0.3.9.5.1", "0.3.9.5.0") is True
    assert is_newer("0.3.9.5.0", "v0.3.9.5.1") is False
    assert is_newer("v1.0.0", "v1.0.0") is False


def test_update_info_find_installer():
    info = UpdateInfo(
        latest_version="0.3.9.5.1",
        assets=[
            ReleaseAsset(name="RobsCodeWizard.exe", download_url="x", size=100),
            ReleaseAsset(name="RobsCodeWizard_Setup.exe", download_url="y", size=200),
        ],
    )
    inst = info.find_installer()
    assert inst is not None and inst.name == "RobsCodeWizard_Setup.exe"


def test_update_info_find_portable_exe():
    info = UpdateInfo(
        latest_version="0.3.9.5.1",
        assets=[
            ReleaseAsset(name="RobsCodeWizard_Setup.exe", download_url="y", size=200),
            ReleaseAsset(name="RobsCodeWizard.exe", download_url="x", size=100),
        ],
    )
    p = info.find_portable_exe()
    assert p is not None and p.name == "RobsCodeWizard.exe"


def test_check_for_update_handles_network_failure():
    def bad(url, timeout=10.0):
        raise URLError("network down")
    assert check_for_update("0.3.9.5.0", "owner/repo", opener=bad) is None


def test_check_for_update_parses_github_release():
    fake = {
        "tag_name": "v0.3.9.5.1",
        "html_url": "https://example/y",
        "body": "Release notes",
        "assets": [
            {"name": "RobsCodeWizard_Setup.exe",
             "browser_download_url": "https://example/setup",
             "size": 12345},
            {"name": "RobsCodeWizard.exe",
             "browser_download_url": "https://example/portable",
             "size": 67890},
        ],
    }

    class FakeResp:
        def __init__(self, data):
            self._data = data
        def read(self):
            return self._data
        def close(self):
            pass

    def opener(url, timeout=10.0):
        return FakeResp(json.dumps(fake).encode("utf-8"))

    info = check_for_update("0.3.9.5.0", "owner/repo", opener=opener)
    assert info is not None
    assert info.latest_version == "0.3.9.5.1"
    assert info.tag_name == "v0.3.9.5.1"
    assert info.is_newer is True
    assert len(info.assets) == 2
    assert info.find_installer().size == 12345


def test_check_for_update_falls_back_on_latest_404():
    """When /releases/latest returns 404, fall back to /releases list."""
    fake_list = [
        {
            "tag_name": "v0.3.9.5.0",
            "html_url": "https://example/y",
            "body": "Notes",
            "draft": False,
            "prerelease": False,
            "assets": [
                {"name": "RobsCodeWizard_Setup.exe",
                 "browser_download_url": "https://example/s", "size": 100},
            ],
        },
    ]

    class FakeResp:
        def __init__(self, data):
            self._data = data
        def read(self):
            return self._data
        def close(self):
            pass

    def opener(url, timeout=10.0):
        if "/releases/latest" in url:
            raise HTTPError(url, 404, "Not Found", {}, None)
        return FakeResp(json.dumps(fake_list).encode("utf-8"))

    info = check_for_update("0.0.0.0", "owner/repo", opener=opener)
    assert info is not None
    assert info.latest_version == "0.3.9.5.0"
    assert info.is_newer is True

