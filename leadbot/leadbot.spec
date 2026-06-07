# PyInstaller spec file for LeadBot Dashboard
# Build a single-file .exe for the web dashboard (no Python required to run)
#
# Build command:
#   pyinstaller --clean leadbot.spec
#
# Output: dist/LeadBotDashboard.exe (~30-40MB)

import sys
from pathlib import Path

block_cipher = None

# Project paths
PROJECT_ROOT = Path(SPECPATH).resolve() if hasattr(sys, '_getframe') else Path('.').resolve()
DASHBOARD_DIR = Path('.').resolve()

# Bundle the dashboard and its templates
a = Analysis(
    ['dashboard.py'],
    pathex=[str(DASHBOARD_DIR)],
    binaries=[],
    datas=[
        # Templates folder (HTML files)
        ('templates', 'templates'),
    ],
    hiddenimports=[
        'uvicorn',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'fastapi',
        'starlette',
        'starlette.applications',
        'starlette.routing',
        'starlette.responses',
        'starlette.requests',
        'starlette.middleware',
        'anyio',
        'sniffio',
        'h11',
        'pydantic',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude heavy stuff that the dashboard doesn't need
        'crawl4ai',
        'playwright',
        'torch',
        'tensorflow',
        'pandas',
        'numpy',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='LeadBotDashboard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Show console for visibility
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
