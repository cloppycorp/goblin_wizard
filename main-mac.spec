# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
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

app = BUNDLE(exe,
         name='Goblin Wizard.app',
         icon='GFX/512logo.icns',
         bundle_identifier=None,
         version='1.0.1',
         info_plist={
            'CFBundleDisplayName': 'Goblin Wizard',
            'CFBundleName': 'Goblin Wizard',
            'NSPrincipalClass': 'NSApplication',
            'NSAppleScriptEnabled': False,
            'UTExportedTypeDeclarations': [
                {
                    'UTTypeIdentifier': 'com.midigoblin.goblinwizard',
                    'UTTypeDescription': 'Goblin Wizard Document',
                    'UTTypeConformsTo': ['public.text'],  # If it's text-based
                    'UTTypeTagSpecification': {
                        # "public.filename-extension": string or array
                        'public.filename-extension': ['goblinwizard'],
                        'public.mime-type': 'text/plain'
                    }
                }
            ],
            'CFBundleDocumentTypes': [
                {
                    'CFBundleTypeName': 'Midi Goblin Wizard File',
                    'CFBundleTypeRole': 'Editor',
                    'CFBundleTypeIconFile': '512logo.icns',
                    'LSItemContentTypes': ['com.midigoblin.goblinwizard'],
                    'LSHandlerRank': 'Owner'
                    }
                ]
            },
         )
