"""v0.3.9.4.1 hotfix patch helper.

Fixes:
  1. _populate_table freeze on large files
     -> wraps the bulk loop with setUpdatesEnabled(False) / setSortingEnabled(False)
        and a busy cursor.
  2. _on_codeset_changed UI freeze
     -> defers the heavy revalidation via QTimer.singleShot so the dropdown
        updates instantly; heavy work moved to _revalidate_and_repopulate.
  3. Bumps app/__init__.py version to 0.3.9.4.1.

Idempotent: safe to re-run.
"""
from __future__ import annotations
import base64
import re
import sys
from pathlib import Path


NEW_POPULATE_B64 = """
ICAgIGRlZiBfcG9wdWxhdGVfdGFibGUoc2VsZik6CiAgICAgICAgIiIidjAuMy45LjQuMTogYnVs
ay11cGRhdGUgZ3VhcmQgKHN1cHByZXNzIHJlcGFpbnRzICsgc29ydCkgZm9yIGJpZyBmaWxlcy4i
IiIKICAgICAgICBmcm9tIFB5U2lkZTYuUXRXaWRnZXRzIGltcG9ydCBRQXBwbGljYXRpb24KICAg
ICAgICBRQXBwbGljYXRpb24uc2V0T3ZlcnJpZGVDdXJzb3IoUXQuV2FpdEN1cnNvcikKICAgICAg
ICBzZWxmLnRhYmxlLnNldFVwZGF0ZXNFbmFibGVkKEZhbHNlKQogICAgICAgIHNlbGYudGFibGUu
c2V0U29ydGluZ0VuYWJsZWQoRmFsc2UpCiAgICAgICAgdHJ5OgogICAgICAgICAgICBzZWxmLnRh
YmxlLnNldFJvd0NvdW50KGxlbihzZWxmLnJvd3MpKQogICAgICAgICAgICBmb3IgaSwgcm93IGlu
IGVudW1lcmF0ZShzZWxmLnJvd3MpOgogICAgICAgICAgICAgICAgcmVzdWx0ID0gc2VsZi5yZXN1
bHRzW2ldCiAgICAgICAgICAgICAgICBzdWdnZXN0aW9uID0gc2VsZi5zdWdnZXN0aW9uc1tpXSBv
ciAiIgogICAgICAgICAgICAgICAgY2VsbHMgPSBbc3RyKHJvdy5nZXQoIlAiLCAiIikpLCBzdHIo
cm93LmdldCgiRCIsICIiKSksIHN0cihyb3cuZ2V0KCJEIiwgIiIpKSwKICAgICAgICAgICAgICAg
ICAgICAgICAgICJZZXMiIGlmIHJlc3VsdFsidmFsaWQiXSBlbHNlICJObyIsCiAgICAgICAgICAg
ICAgICAgICAgICAgICAiOyAiLmpvaW4ocmVzdWx0WyJpc3N1ZXMiXSksICIiLCBzdWdnZXN0aW9u
XQogICAgICAgICAgICAgICAgZm9yIGMsIHZhbHVlIGluIGVudW1lcmF0ZShjZWxscyk6CiAgICAg
ICAgICAgICAgICAgICAgaXRlbSA9IFFUYWJsZVdpZGdldEl0ZW0odmFsdWUpOyBpdGVtLnNldFRl
eHRBbGlnbm1lbnQoUXQuQWxpZ25DZW50ZXIpCiAgICAgICAgICAgICAgICAgICAgc2VsZi50YWJs
ZS5zZXRJdGVtKGksIGMsIGl0ZW0pCiAgICAgICAgICAgICAgICBzZWxmLl9hcHBseV9yb3dfY29s
b3IoaSwgcm93LCByZXN1bHQpCiAgICAgICAgZmluYWxseToKICAgICAgICAgICAgc2VsZi50YWJs
ZS5zZXRTb3J0aW5nRW5hYmxlZChUcnVlKQogICAgICAgICAgICBzZWxmLnRhYmxlLnNldFVwZGF0
ZXNFbmFibGVkKFRydWUpCiAgICAgICAgICAgIHNlbGYudGFibGUudmlld3BvcnQoKS51cGRhdGUo
KQogICAgICAgICAgICBRQXBwbGljYXRpb24ucmVzdG9yZU92ZXJyaWRlQ3Vyc29yKCkKICAgICAg
ICBzZWxmLnRhYmxlLnJlc2l6ZUNvbHVtbnNUb0NvbnRlbnRzKCkKCg==
"""
NEW_CODESET_B64 = """
ICAgIGRlZiBfb25fY29kZXNldF9jaGFuZ2VkKHNlbGYsIG5hbWU6IHN0cik6CiAgICAgICAgIiIi
djAuMy45LjQuMTogZGVmZXIgcmV2YWxpZGF0aW9uIHNvIHRoZSBkcm9wZG93biB1cGRhdGVzIGlu
c3RhbnRseS4iIiIKICAgICAgICB0cnk6CiAgICAgICAgICAgIGxvZy5pbmZvKCJDb2RlIHNldCBz
d2l0Y2hpbmc6ICVzIC0+ICVzIiwgc2VsZi5jb2Rlc2V0Lm5hbWUsIG5hbWUpCiAgICAgICAgICAg
IHNldF9zZXR0aW5nKCJhY3RpdmVfY29kZXNldCIsIG5hbWUpCiAgICAgICAgICAgIHNlbGYuc2V0
dGluZ3NbImFjdGl2ZV9jb2Rlc2V0Il0gPSBuYW1lCiAgICAgICAgICAgIHNlbGYuY29kZXNldCA9
IGxvYWRfY2F0YWxvZyhuYW1lKQogICAgICAgICAgICBpZiBzZWxmLnJvd3M6CiAgICAgICAgICAg
ICAgICBmcm9tIFB5U2lkZTYuUXRDb3JlIGltcG9ydCBRVGltZXIKICAgICAgICAgICAgICAgIFFU
aW1lci5zaW5nbGVTaG90KDAsIHNlbGYuX3JldmFsaWRhdGVfYW5kX3JlcG9wdWxhdGUpCiAgICAg
ICAgZXhjZXB0IEV4Y2VwdGlvbiBhcyBleGM6CiAgICAgICAgICAgIGxvZy5leGNlcHRpb24oIkNv
ZGUgc2V0IHN3aXRjaCBmYWlsZWQ6ICVzIiwgZXhjKQogICAgICAgICAgICBzZWxmLl9lcnJvcl9k
aWFsb2coIkNvZGUgc2V0IHN3aXRjaCBmYWlsZWQiLCBleGMpCgogICAgZGVmIF9yZXZhbGlkYXRl
X2FuZF9yZXBvcHVsYXRlKHNlbGYpOgogICAgICAgICIiInYwLjMuOS40LjE6IGhlYXZ5IHdvcmsg
c3BsaXQgb3V0IHNvIGl0IHJ1bnMgYWZ0ZXIgdGhlIFVJIHJlZHJhd3MuIiIiCiAgICAgICAgdHJ5
OgogICAgICAgICAgICBpZiBub3Qgc2VsZi5yb3dzOgogICAgICAgICAgICAgICAgcmV0dXJuCiAg
ICAgICAgICAgIHNlbGYucmVzdWx0cyA9IHZhbGlkYXRlX3Jvd3Moc2VsZi5yb3dzLCBzZWxmLmNv
ZGVzZXQpCiAgICAgICAgICAgIHNlbGYuc3VnZ2VzdGlvbnMgPSBidWlsZF9zdWdnZXN0aW9ucyhz
ZWxmLnJvd3MsIHNlbGYuY29kZXNldCwgc2VsZi5yZXN1bHRzKQogICAgICAgICAgICBzZWxmLl9w
b3B1bGF0ZV90YWJsZSgpCiAgICAgICAgZXhjZXB0IEV4Y2VwdGlvbiBhcyBleGM6CiAgICAgICAg
ICAgIGxvZy5leGNlcHRpb24oIlJldmFsaWRhdGlvbiBmYWlsZWQ6ICVzIiwgZXhjKQogICAgICAg
ICAgICBzZWxmLl9lcnJvcl9kaWFsb2coIlJldmFsaWRhdGlvbiBmYWlsZWQiLCBleGMpCgo=
"""

NEW_POPULATE = base64.b64decode(NEW_POPULATE_B64.replace("\n", "")).decode("utf-8")
NEW_CODESET = base64.b64decode(NEW_CODESET_B64.replace("\n", "")).decode("utf-8")


def patch_main_window() -> None:
    p = Path("app/ui/main_window.py")
    src = p.read_text(encoding="utf-8")
    orig = src

    # --- Replace _populate_table ---
    pat_pop = re.compile(
        r"^    def _populate_table\(self\):.*?(?=^    def |\Z)",
        re.DOTALL | re.MULTILINE,
    )
    if not pat_pop.search(src):
        print("  [ERROR] _populate_table method not found.")
        sys.exit(2)

    if "setUpdatesEnabled(False)" in pat_pop.search(src).group(0):
        print("  _populate_table already patched (skipping).")
    else:
        src = pat_pop.sub(NEW_POPULATE, src, count=1)
        print("  Patched: _populate_table")

    # --- Replace _on_codeset_changed (and add _revalidate_and_repopulate) ---
    pat_cs = re.compile(
        r"^    def _on_codeset_changed\(self, name: str\):.*?(?=^    def |\Z)",
        re.DOTALL | re.MULTILINE,
    )
    if not pat_cs.search(src):
        print("  [ERROR] _on_codeset_changed method not found.")
        sys.exit(3)

    if "_revalidate_and_repopulate" in src:
        print("  _on_codeset_changed already patched (skipping).")
    else:
        src = pat_cs.sub(NEW_CODESET, src, count=1)
        print("  Patched: _on_codeset_changed + added _revalidate_and_repopulate")

    if src == orig:
        print("  No changes (already patched).")
    else:
        p.write_text(src, encoding="utf-8")
        print(f"  Wrote: {p}")


def bump_version() -> None:
    p = Path("app/__init__.py")
    src = p.read_text(encoding="utf-8")
    new = re.sub(
        r'__version__\s*=\s*"[^"]*"',
        '__version__ = "0.3.9.4.1"',
        src,
    )
    if new == src:
        if '"0.3.9.4.1"' in src:
            print("  Version already 0.3.9.4.1 (skipping).")
        else:
            print("  [WARN] could not find __version__ to bump.")
    else:
        p.write_text(new, encoding="utf-8")
        print("  Bumped: app/__init__.py -> 0.3.9.4.1")


def main() -> None:
    print("  Patching app/ui/main_window.py...")
    patch_main_window()
    print("  Bumping app/__init__.py...")
    bump_version()
    print("  Done.")


if __name__ == "__main__":
    main()
