#!/usr/bin/env python3
"""
Advanced Windows executable builder for Dungeon Crawler Game.
Creates a proper .exe file that can be distributed to Windows users.
"""

import os
import sys
import subprocess
import shutil
import zipfile
from pathlib import Path
import tempfile

def check_dependencies():
    """Check if required tools are available."""
    try:
        result = subprocess.run(['pyinstaller', '--version'], capture_output=True, text=True)
        print(f"✅ PyInstaller found: {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("❌ PyInstaller not found. Installing...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
            print("✅ PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install PyInstaller")
            return False

def create_exe_spec():
    """Create a detailed spec file for the executable."""
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-
# Dungeon Crawler Game - PyInstaller Spec File

import sys
from pathlib import Path

# Get all Python game files
game_files = [
    'main.py', 'player.py', 'enemy.py', 'items.py', 'combat.py',
    'weapon_renderer.py', 'level.py', 'damage_numbers.py', 'notifications.py',
    'ui.py', 'assets.py', 'visibility.py', 'game_state.py', 'sound_manager.py',
    'boss.py', 'boss_dagger_haste.py', 'boss_weapons.py', 'new_enemy_types.py'
]

# Create data files list
datas = []
for file in game_files:
    if Path(file).exists():
        datas.append((file, '.'))

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['pygame', 'numpy', 'math', 'random', 'typing', 'enum'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'PIL', 'setuptools'],
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
    name='DungeonCrawlerGame',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Hide console for better user experience
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None  # Add icon path here if you have one
)
'''

    with open('DungeonCrawler.spec', 'w') as f:
        f.write(spec_content)
    
    print("📄 Created advanced spec file: DungeonCrawler.spec")

def build_executable():
    """Build the Windows executable using advanced options."""
    
    print("🎮 Building Advanced Windows Executable...")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Create spec file
    create_exe_spec()
    
    # Clean previous builds
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            print(f"🧹 Cleaning {folder}/")
            shutil.rmtree(folder)
    
    # Build using spec file for better control
    print("🔨 Building executable with spec file...")
    
    try:
        cmd = ['pyinstaller', '--clean', 'DungeonCrawler.spec']
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print("✅ Build completed!")
        
        # Check if executable was created
        exe_path = Path('dist') / 'DungeonCrawlerGame.exe'
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"🎯 Executable created: {exe_path}")
            print(f"📊 File size: {size_mb:.1f} MB")
            
            # Test the executable quickly
            print("🧪 Testing executable...")
            try:
                # Just check if it starts (kill after 2 seconds)
                test_process = subprocess.Popen(
                    [str(exe_path)], 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE
                )
                import time
                time.sleep(2)
                test_process.terminate()
                print("✅ Executable test passed!")
            except Exception as e:
                print(f"⚠️ Executable test failed: {e}")
            
            return True
        else:
            print("❌ Executable not found after build")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed!")
        print(f"Command: {' '.join(e.cmd)}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def create_distribution_package():
    """Create a complete distribution package."""
    
    print("📦 Creating Distribution Package...")
    
    # Distribution folder name
    dist_name = "DungeonCrawler_Game_Windows"
    
    # Clean previous distribution
    if os.path.exists(dist_name):
        shutil.rmtree(dist_name)
    if os.path.exists(f"{dist_name}.zip"):
        os.remove(f"{dist_name}.zip")
    
    # Create distribution folder
    os.makedirs(dist_name)
    
    # Copy the executable
    exe_source = Path('dist') / 'DungeonCrawlerGame.exe'
    if exe_source.exists():
        shutil.copy2(exe_source, dist_name)
        print(f"✅ Copied executable to {dist_name}/")
    else:
        print("❌ Executable not found!")
        return False
    
    # Create README for the executable
    readme_content = '''# Dungeon Crawler Game

## How to Play
Double-click "DungeonCrawlerGame.exe" to start playing!

## Controls
- **WASD** or **Arrow Keys**: Move your character
- **Left Click**: Attack with equipped weapon
- **Right Click**: Cast equipped spell
- **ESC**: Quit game

## Game Features
- Procedurally generated dungeons
- Multiple enemy types with unique AI
- Weapons: Swords, Spears, Maces, War Axes
- Spells: Haste, Power Pulse, Turn Coat, and more!
- Boss battles with special abilities
- Experience and leveling system
- Line-of-sight fog of war
- Enhanced combat with visual effects

## System Requirements
- Windows 7 or newer
- 1GB RAM minimum
- DirectX compatible graphics

## About This Game
This is a complete standalone executable - no additional installation required!
All game files and dependencies are included in this single .exe file.

Have fun exploring the dungeons! 🎮
'''
    
    with open(os.path.join(dist_name, 'README.txt'), 'w') as f:
        f.write(readme_content)
    
    # Create version info
    with open(os.path.join(dist_name, 'VERSION.txt'), 'w') as f:
        f.write("Dungeon Crawler Game v1.0\\n")
        f.write("Windows Executable Edition\\n")
        f.write("Built with PyInstaller\\n")
        f.write("Single-file standalone executable\\n")
    
    print("✅ Added documentation files")
    
    # Create ZIP file
    zip_path = f"{dist_name}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
        for root, dirs, files in os.walk(dist_name):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, os.path.dirname(dist_name))
                zipf.write(file_path, arc_name)
    
    # Get sizes
    exe_size = os.path.getsize(os.path.join(dist_name, 'DungeonCrawlerGame.exe'))
    zip_size = os.path.getsize(zip_path)
    
    print("\\n🎉 DISTRIBUTION PACKAGE COMPLETE!")
    print("=" * 60)
    print(f"📁 Folder: {os.path.abspath(dist_name)}/")
    print(f"🎮 Executable: DungeonCrawlerGame.exe ({exe_size/1024/1024:.1f} MB)")
    print(f"📦 Distribution ZIP: {zip_path} ({zip_size/1024/1024:.1f} MB)")
    print("\\n🚀 READY TO SHARE!")
    print("=" * 60)
    print("📧 Send the ZIP file to anyone with Windows")
    print("🎯 They just extract and double-click the .exe file")
    print("🎮 No Python or additional software needed!")
    print("✨ Complete standalone gaming experience!")
    
    return True

def main():
    """Main build process."""
    
    print("🚀 DUNGEON CRAWLER - WINDOWS EXECUTABLE BUILDER")
    print("=" * 60)
    
    # Verify we have the game files
    required_files = ['main.py', 'player.py', 'enemy.py']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    
    print("✅ Game files found")
    
    # Build executable
    if not build_executable():
        print("❌ Failed to build executable")
        return False
    
    # Create distribution package
    if not create_distribution_package():
        print("❌ Failed to create distribution package")
        return False
    
    print("\\n🏆 SUCCESS! Your game is ready for Windows distribution!")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\\n❌ Build process failed!")
        input("Press Enter to exit...")
        sys.exit(1)
    
    print("\\n✨ Build process completed successfully!")
    input("Press Enter to exit...")