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
        ('gateway',                'gateway'),
        ('gateway/static',         'gateway/static'),
        ('registry',               'registry'),
        ('security',               'security'),
        ('ui',                     'ui'),
    ],
    hiddenimports=[
        # uvicorn
        'uvicorn', 'uvicorn.logging', 'uvicorn.loops', 'uvicorn.loops.auto',
        'uvicorn.protocols', 'uvicorn.protocols.http', 'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets', 'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan', 'uvicorn.lifespan.on',

        # fastapi & friends
        'fastapi', 'starlette', 'starlette.routing', 'starlette.staticfiles',
        'pydantic', 'pydantic.deprecated.class_validators',
        'dotenv', 'anyio', 'anyio._backends._asyncio',
        'httpx', 'sse_starlette', 'aiofiles',

        # desktop
        'PIL', 'PIL.Image', 'PIL.ImageDraw',
        'pystray',

        # analytics
        'posthog', 'posthog.client', 'posthog.request',

        # gateway
        'gateway', 'gateway.main', 'gateway.router', 'gateway.models',
        'gateway.proxy', 'gateway.transport', 'gateway.transport.sse',
        'gateway.analytics', 'gateway.server_manager', 'gateway.cli_entry',

        # registry & security
        'registry', 'registry.registry', 'registry.validator',
        'security', 'security.auth', 'security.audit',
        'security.policy', 'security.rate_limiter',

        # all template servers (so PyInstaller bundles them)
        'templates',
        'templates.qa', 'templates.qa.jira_server', 'templates.qa.testrail_server',
        'templates.qa.pytest_server', 'templates.qa.xray_server',
        'templates.qa.playwright_server', 'templates.qa.allure_server',
        'templates.qa.selenium_server',
        'templates.dev', 'templates.dev.github_server', 'templates.dev.git_server',
        'templates.dev.azure_devops_server', 'templates.dev.code_runner_server',
        'templates.dev.confluence_server', 'templates.dev.linear_server',
        'templates.dev.gitlab_server',
        'templates.general', 'templates.general.slack_server',
        'templates.general.filesystem_server', 'templates.general.rest_api_server',
        'templates.general.web_search_server', 'templates.general.database_server',
        'templates.general.notion_server', 'templates.general.asana_server',
        'templates.general.google_sheets_server', 'templates.general.figma_server',
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
