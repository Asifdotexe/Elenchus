# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller build specification for Elenchus standalone binary."""

import os
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

# Locate root directory relative to this spec file
spec_dir = os.path.dirname(os.path.abspath(SPEC))
project_root = os.path.abspath(os.path.join(spec_dir, ".."))
main_script = os.path.join(project_root, "main.py")

# Collect package data and dynamic libraries
datas = collect_data_files("faster_whisper")
icon_file = os.path.join(project_root, "assets", "branding", "kit", "favicon.ico")
if os.path.exists(icon_file):
    datas.append((icon_file, "assets/branding/kit"))

binaries = collect_dynamic_libs("ctranslate2") + collect_dynamic_libs("sounddevice")

a = Analysis(
    [main_script],
    pathex=[project_root],
    binaries=binaries,
    datas=datas,
    hiddenimports=[
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtWidgets",
        "PyQt6.QtSvg",
        "ctranslate2",
        "faster_whisper",
        "sounddevice",
        "numpy",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "matplotlib",
        "scipy",
        "pandas",
        "PIL",
        "IPython",
        "notebook",
        "pytest",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

# Single-file standalone binary (direct curl download target)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="elenchus",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file if os.path.exists(icon_file) else None,
)
