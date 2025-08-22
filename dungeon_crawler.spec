# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('game_src', 'game_src'),
        ('assets', 'assets'),
    ],
    hiddenimports=[
        'game_src.main',
        'game_src.player', 
        'game_src.level',
        'game_src.enemy',
        'game_src.boss',
        'game_src.boss_weapons',
        'game_src.boss_dagger_haste', 
        'game_src.new_enemy_types',
        'game_src.combat',
        'game_src.items',
        'game_src.ui',
        'game_src.assets',
        'game_src.visibility',
        'game_src.sound_manager',
        'game_src.game_state',
        'game_src.weapon_renderer',
        'game_src.damage_numbers',
        'game_src.notifications'
    ],
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
    name='DungeonCrawler',
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
    icon=None,
)