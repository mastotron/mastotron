# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['cli.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'eventlet.hubs.epolls',
        'eventlet.hubs.kqueue',
        'eventlet.hubs.selects',
        'dns', 
        'dns.dnssec',
        'dns.e164',
        'dns.hash',
        'dns.namedict',
        'dns.tsigkeyring',
        'dns.update',
        'dns.version',
        'dns.asyncquery',
        'dns.asyncresolver',
        'dns.versioned',
        'dns.zone'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

a.datas += Tree('mastotron/gui/static', 'mastotron/gui/static')
a.datas += Tree('mastotron/gui/templates', 'mastotron/gui/templates')

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MastotronApp',
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
)


app = BUNDLE(
    exe,
    name='MastotronApp.app',
    appname='MastotronApp',
    icon=None,
    bundle_identifier=None,
)

######################################
# https://github.com/pyinstaller/pyinstaller/issues/5154#issuecomment-690772204
##
try:
    print(app)
    print(app.name, app.appname)

    ## Make app bundle double-clickable
    import plistlib
    from pathlib import Path
    app_path = Path(app.name)

    # read Info.plist
    with open(app_path / 'Contents/Info.plist', 'rb') as f:
        pl = plistlib.load(f)

    # write Info.plist
    with open(app_path / 'Contents/Info.plist', 'wb') as f:
        pl['CFBundleExecutable'] = 'wrapper'
        plistlib.dump(pl, f)

    # write new wrapper script
    shell_script = """#!/bin/bash
    dir=$(dirname $0)
    open -a Terminal file://${dir}/%s""" % app.appname
    with open(app_path / 'Contents/MacOS/wrapper', 'w') as f:
        f.write(shell_script)

    # make it executable
    (app_path  / 'Contents/MacOS/wrapper').chmod(0o755)
    ######################################
except Exception as e:
    print('!!',e,'!!','skipping,,,')
    pass