name: Build and Release

on:
  push:
    tags:
      - 'v*.*.*'
      - 'v*.*.*.*'

permissions:
  contents: write

jobs:
  build:
    name: Build EXE + Installer on Windows
    runs-on: windows-latest

    steps:
      # ----------------------------------------------------------
      # Checkout the tagged commit
      # ----------------------------------------------------------
      - name: Checkout source
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      # ----------------------------------------------------------
      # Set up Python
      # ----------------------------------------------------------
      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'

      # ----------------------------------------------------------
      # Install dependencies
      # ----------------------------------------------------------
      - name: Install Python dependencies
        shell: cmd
        run: |
          python -m pip install --upgrade pip
          if exist requirements.txt pip install -r requirements.txt
          pip install pyinstaller

      # ----------------------------------------------------------
      # Run tests (non-blocking-friendly; remove '|| exit 0' to enforce)
      # ----------------------------------------------------------
      - name: Run pytest
        shell: cmd
        run: |
          if exist tests (
            pip install pytest
            pytest -q
          ) else (
            echo No tests/ folder, skipping.
          )

      # ----------------------------------------------------------
      # Build EXE with PyInstaller (onefile, windowed)
      # Expects entry point at app/main.py and icon at assets/icon.ico
      # ----------------------------------------------------------
      - name: Build EXE (PyInstaller onefile windowed)
        shell: cmd
        run: |
          set ICON_ARG=
          if exist assets\icon.ico set ICON_ARG=--icon assets\icon.ico

          set DATA_ARGS=
          if exist assets   set DATA_ARGS=!DATA_ARGS! --add-data "assets;assets"
          if exist data     set DATA_ARGS=!DATA_ARGS! --add-data "data;data"
          if exist catalogs set DATA_ARGS=!DATA_ARGS! --add-data "catalogs;catalogs"

          pyinstaller --noconfirm --onefile --windowed ^
            --name RobsCodeWizard ^
            %ICON_ARG% %DATA_ARGS% ^
            app\main.py
        env:
          PYTHONIOENCODING: utf-8

      # ----------------------------------------------------------
      # Install Inno Setup (Chocolatey) and build the installer
      # Expects build/installer.iss in the repo
      # ----------------------------------------------------------
      - name: Install Inno Setup
        shell: cmd
        run: choco install innosetup -y --no-progress

      - name: Build Installer (Inno Setup)
        shell: cmd
        run: |
          if not exist build\installer.iss (
            echo [ERROR] build\installer.iss not found.
            exit /b 1
          )
          "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" build\installer.iss

      # ----------------------------------------------------------
      # Collect artifacts to a single staging folder
      # ----------------------------------------------------------
      - name: Stage release artifacts
        shell: cmd
        run: |
          if not exist release mkdir release
          if exist dist\RobsCodeWizard.exe        copy /Y dist\RobsCodeWizard.exe        release\
          if exist dist\RobsCodeWizard_Setup.exe  copy /Y dist\RobsCodeWizard_Setup.exe  release\
          dir release

      # ----------------------------------------------------------
      # Upload artifacts to the workflow run (for debugging)
      # ----------------------------------------------------------
      - name: Upload workflow artifacts
        uses: actions/upload-artifact@v4
        with:
          name: RobsCodeWizard-${{ github.ref_name }}
          path: release/*

      # ----------------------------------------------------------
      # Create / update the GitHub Release and attach binaries
      # ----------------------------------------------------------
      - name: Publish GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          name: Rob's Code Wizard ${{ github.ref_name }}
          tag_name: ${{ github.ref_name }}
          generate_release_notes: true
          files: |
            release/RobsCodeWizard.exe
            release/RobsCodeWizard_Setup.exe