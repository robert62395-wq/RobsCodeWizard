import json, hashlib
from io import BytesIO
import pytest
from app.services.updater import (parse_version, is_newer, fetch_manifest,
    check_for_update, download_update, verify_sha256, apply_update_hint, UpdateInfo)


class _H:
    def __init__(self, d): self._d = d
    def get(self, k, default=None): return self._d.get(k, default)


class FakeResp:
    def __init__(self, data, headers=None):
        self._buf = BytesIO(data); self._h = headers or {}
    def read(self, n=-1): return self._buf.read(n) if n != -1 else self._buf.read()
    def info(self): return _H(self._h)
    def close(self): self._buf.close()


def mk(data, headers=None, raise_exc=None):
    def _op(url, timeout=5.0):
        if raise_exc: raise raise_exc
        payload = data if isinstance(data, bytes) else data.encode("utf-8")
        return FakeResp(payload, headers)
    return _op


def test_parse_version():
    assert parse_version("0.3.9.3") == (0,3,9,3)


def test_is_newer():
    assert is_newer("0.3.9.3", "0.3.9.2") is True


def test_fetch_manifest():
    p = {"latest_version":"1.2.3","download_url":"https://x/y.zip"}
    assert fetch_manifest("https://x", opener=mk(json.dumps(p))) == p


def test_check_newer():
    p = {"latest_version":"9.9.9","download_url":"https://x/y.zip"}
    info = check_for_update("0.3.9.3","https://x", opener=mk(json.dumps(p)))
    assert info.is_newer is True


def test_check_net_err():
    assert check_for_update("0.3.9.3","https://x", opener=mk(b"", raise_exc=OSError("no"))) is None


def test_download_writes(tmp_path):
    p = b"ZIP"
    info = UpdateInfo(latest_version="9", download_url="https://x/y.zip")
    out = download_update(info, tmp_path, opener=mk(p))
    assert out.read_bytes() == p


def test_verify_sha(tmp_path):
    p = tmp_path / "x.bin"; p.write_bytes(b"hello")
    assert verify_sha256(p, hashlib.sha256(b"hello").hexdigest()) is True


def test_apply_hint(tmp_path):
    p = tmp_path / "u.zip"; p.write_bytes(b"x")
    assert str(p) in apply_update_hint(p)
