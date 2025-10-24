# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 需要包含的数据文件
added_files = [
    ('weights', 'weights'),
    ('demo.yaml', '.'),
]

# 需要包含的隐藏导入
hiddenimports = [
    'pdf2docx',
    'fitz',
    'torch',
    'torchvision',
    'PIL',
    'docx',
    'yaml',
    'numpy',
    'cv2',
    'ultralytics',
    'doclayout_yolo',
    'unimernet',
]

a = Analysis(
    ['freep2w.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=hiddenimports,
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
    [],
    exclude_binaries=True,
    name='freep2w',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='freep2w',
)
