# -*- mode: python ; coding: utf-8 -*-


datas = [
    ('assets', 'assets'),
    ('docs', 'docs'),
]
binaries = []
hiddenimports = [
    'openpyxl',
    'openpyxl.cell._writer',
]


a = Analysis(
    ['visualizador.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'pytest',
        'pandas.tests',
        'numpy.tests',
        'PyQt5.Qt3DAnimation',
        'PyQt5.Qt3DCore',
        'PyQt5.Qt3DExtras',
        'PyQt5.Qt3DInput',
        'PyQt5.Qt3DLogic',
        'PyQt5.Qt3DRender',
        'PyQt5.QtWebEngine',
        'PyQt5.QtWebEngineCore',
        'PyQt5.QtWebEngineWidgets',
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='BGA Mapper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    icon='assets\\logo.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='BGA Mapper',
)

