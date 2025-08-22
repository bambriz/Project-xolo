#!/usr/bin/env python3
"""
Build script to create Windows executable for the dungeon crawler game.
Creates a standalone executable that includes all dependencies.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_executable():
    """Build the game executable using PyInstaller."""
    
    print("🎮 Building Dungeon Crawler Game Executable...")
    print("=" * 50)
    
    # Check if main.py exists
    if not os.path.exists("main.py"):
        print("❌ Error: main.py not found!")
        return False
    
    # Clean previous builds
    if os.path.exists("dist"):
        print("🧹 Cleaning previous build...")
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",  # Create single executable file
        "--windowed",  # Hide console window (for cleaner experience)
        "--name=DungeonCrawler",  # Name of the executable
        "--icon=NONE",  # No icon for now
        "--collect-all=pygame",  # Include all pygame data
        "--hidden-import=pygame",
        "--hidden-import=numpy",
        "--add-data=*.py:.",  # Include all Python files
        "main.py"
    ]
    
    print("🔨 Running PyInstaller...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✅ Build successful!")
        
        # Check if executable was created
        exe_path = Path("dist") / "DungeonCrawler.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"📦 Executable created: {exe_path}")
            print(f"📊 File size: {size_mb:.1f} MB")
            
            # Create a simple README for distribution
            readme_content = """# Dungeon Crawler Game

## How to Play
1. Double-click DungeonCrawler.exe to start the game
2. Use WASD or arrow keys to move
3. Left-click to attack with melee weapons
4. Right-click to cast spells
5. Collect items, defeat enemies, and progress through levels!

## Controls
- WASD / Arrow Keys: Move
- Left Click: Melee attack
- Right Click: Cast spell/ability
- ESC: Quit game

## System Requirements
- Windows 7 or newer
- No additional software required - everything is included!

Enjoy the game! 🎮
"""
            
            with open("dist/README.txt", "w") as f:
                f.write(readme_content)
            
            print("📝 README.txt created in dist/ folder")
            print("\n🎉 Build complete! Your game is ready to distribute.")
            print(f"📁 Find your executable in: {os.path.abspath('dist')}")
            print("\n💡 You can now:")
            print("   1. Test the game by running dist/DungeonCrawler.exe")
            print("   2. Zip the dist/ folder and send it to anyone")
            print("   3. The game will run on any Windows computer!")
            
            return True
        else:
            print("❌ Error: Executable not found after build")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed!")
        print(f"Error: {e}")
        print(f"Output: {e.output}")
        print(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def create_spec_file():
    """Create a custom spec file for more control over the build."""
    
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('*.py', '.'),
    ],
    hiddenimports=['pygame', 'numpy'],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DungeonCrawler',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Hide console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""
    
    with open("DungeonCrawler.spec", "w") as f:
        f.write(spec_content)
    
    print("📄 Created DungeonCrawler.spec file for custom builds")

if __name__ == "__main__":
    print("🚀 Dungeon Crawler Game - Executable Builder")
    print("This will create a Windows executable (.exe) file")
    print()
    
    # Create spec file for future use
    create_spec_file()
    
    # Build the executable
    success = build_executable()
    
    if success:
        print("\n" + "=" * 50)
        print("🎊 SUCCESS! Your game is ready to share!")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("❌ Build failed. Check the error messages above.")
        print("=" * 50)
        sys.exit(1)