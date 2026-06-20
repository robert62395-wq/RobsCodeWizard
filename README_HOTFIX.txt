Rob's Code Wizard - v0.4.1.1 Hotfix
====================================

WHAT BROKE
----------
The Phase 1 overlay shipped an empty overlay/app/__init__.py to mark the
package directory. When apply_phase_1.bat ran xcopy, it overwrote your
existing app/__init__.py (which defined __version__) with the empty file.

This broke test collection for any module that imports __version__ from
the app package - e.g. tests/test_report_exporter.py:

    ImportError: cannot import name '__version__' from 'app'

WHAT THIS HOTFIX DOES
---------------------
Restores app/__init__.py with a version-from-file loader:

    from pathlib import Path
    _VERSION_FILE = Path(__file__).parent.parent / "resources" / "version.txt"
    __version__ = _VERSION_FILE.read_text(encoding="utf-8").strip()

This keeps __version__ in sync with resources/version.txt automatically,
so every future phase bump (v0.4.2, v0.4.3, ...) updates __version__
without touching app/__init__.py at all.

RUN ORDER
---------
1. Extract this zip into the Robs_Code_Wizard project root
2. apply_hotfix.bat   - restores __init__.py + verifies tests collect/run
3. push_hotfix.bat    - commits, tags v0.4.1.1, pushes main + tag

NEW RULE GOING FORWARD
----------------------
Phase overlay zips will NEVER ship a top-level app/__init__.py or any
existing __init__.py unless the change is intentional and called out
in the changelog. New subpackages will still ship their own
__init__.py files (e.g. app/services/__init__.py for new packages),
but only when that subpackage is genuinely new.
