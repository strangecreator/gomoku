# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

options = [('W ignore', None, 'OPTION')]

a = Analysis(
    ['src/client/interfaces/GUI/gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/client/config.json', 'src/client'),
        ('src/client/config_loader.py', 'src/client'),
        ('src/client/connection/connection.py', 'src/client/connection'),
        ('src/client/game_logic/game_logic.py', 'src/client/game_logic'),
        ('dev', 'dev')
    ],
    hiddenimports=["requests", "pygame"],
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
