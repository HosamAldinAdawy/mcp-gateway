# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['launcher.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('registry/registry.json', 'registry'),
        ('security/policy.json',   'security'),
        ('.env.example',           '.'),
        ('templates',              'templates'),
    ],
    hiddenimports=[
        'uvicorn', 'uvicorn.logging', 'uvicorn.loops', 'uvicorn.loops.auto',
        'uvicorn.protocols', 'uvicorn.protocols.http', 'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets', 'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan', 'uvicorn.lifespan.on',
        'fastapi', 'starlette', 'starlette.routing', 'starlette.staticfiles',
        'pydantic', 'pydantic.deprecated.class_validators',
        'dotenv', 'anyio', 'anyio._backends._asyncio',
        'httpx', 'sse_starlette', 'aiofiles',
        'PIL', 'PIL.Image', 'PIL.ImageDraw',
        'pystray',
        'gateway', 'gateway.main', 'gateway.router', 'gateway.models',
        'gateway.proxy', 'gateway.transport', 'gateway.transport.sse',
        'registry', 'registry.registry', 'registry.validator',
        'security', 'security.auth', 'security.audit',
        'security.policy', 'security.rate_limiter',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'PyQt5'],
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='mcp-gateway',
    debug=False,
    strip=False,
    upx=True,
    console=True,
    windowed=False,
)
