Rob's Code Wizard v0.3.9.4.1 HOTFIX
====================================

WHAT IT FIXES
-------------
  1. UI freeze when opening a large file or switching codesets.
     _populate_table now suppresses Qt repaints + sorting during bulk
     updates (setUpdatesEnabled / setSortingEnabled guards).

  2. Codeset dropdown freeze (ODOT -> VDT on a VDT-format file).
     The heavy revalidation work is now deferred via QTimer.singleShot
     so the dropdown updates instantly; revalidation runs immediately
     after on the event loop.

  3. Bumps version to 0.3.9.4.1.

CONTENTS
--------
  apply_v0_3_9_4_1_hotfix.bat   - One-click hotfix applier
  _apply_hotfix1.py             - Python helper (called by the .bat)
  README.txt                    - This file

HOW TO USE
----------
  1. Extract BOTH files (.bat and .py) into the ROOT of your
     v0.3.9.4 working folder so they sit next to the app\ folder.
  2. Open a Command Prompt in that folder.
  3. Run:
       apply_v0_3_9_4_1_hotfix.bat
  4. Expected ending banner:
       SUCCESS - v0.3.9.4.1 hotfix applied.

VERIFY THE FIX
--------------
  1. .venv\Scripts\activate
  2. python launcher.py
  3. Open a VDT-format point file while codeset is ODOT.
  4. Change dropdown to VDT.
  5. The dropdown should update instantly; the table refresh should
     complete in a second or two; the app should NOT freeze.

REBUILD + RELEASE
-----------------
  1. pyinstaller --noconfirm --onefile --windowed --name RobsCodeWizard --add-data "resources;resources" app\main.py
  2. dist\RobsCodeWizard.exe   (smoke test)
  3. git add -A
  4. git commit -m "v0.3.9.4.1: populate_table + codeset hotfix"
  5. git push
  6. tag_release.bat   (enter v0.3.9.4.1 when prompted)

ROLLBACK
--------
  copy /Y app\ui\main_window.py.hotfix1.bak app\ui\main_window.py
  copy /Y app\__init__.py.hotfix1.bak app\__init__.py
