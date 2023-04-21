# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

options = [('W ignore', None, 'OPTION')]

a = Analysis(
    ['interfaces/graphic/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.json', '.'),
        ('config_loader.py', '.'),
        ('connection/main.py', 'connection'),
        ('game_logic/main.py', 'game_logic'),
        ('interfaces/graphic/src', 'interfaces/graphic/src')
    ],
    hiddenimports=["requests"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    options,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='gomoku',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
