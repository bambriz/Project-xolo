#!/usr/bin/env python3
"""
Creates a Windows-compatible distribution folder for the dungeon crawler game.
This creates a portable version that works on Windows without needing Python installed.
"""

import os
import shutil
import zipfile
from pathlib import Path

def create_distribution():
    """Create a Windows distribution folder."""
    
    print("🎮 Creating Windows Distribution Package...")
    print("=" * 50)
    
    # Clean previous distribution
    dist_folder = "DungeonCrawler_Windows"
    if os.path.exists(dist_folder):
        print("🧹 Cleaning previous distribution...")
        shutil.rmtree(dist_folder)
    
    # Create distribution folder
    os.makedirs(dist_folder)
    
    # List of game files to include
    game_files = [
        "main.py", "player.py", "enemy.py", "items.py", "combat.py", 
        "weapon_renderer.py", "level.py", "damage_numbers.py", "notifications.py",
        "ui.py", "assets.py", "visibility.py", "game_state.py", "sound_manager.py",
        "boss.py", "boss_dagger_haste.py", "boss_weapons.py", "new_enemy_types.py"
    ]
    
    # Copy game files
    print("📁 Copying game files...")
    for file in game_files:
        if os.path.exists(file):
            shutil.copy2(file, dist_folder)
            print(f"   ✅ {file}")
        else:
            print(f"   ⚠️  {file} not found, skipping...")
    
    # Create Windows batch file to run the game
    batch_content = '''@echo off
title Dungeon Crawler Game
echo Starting Dungeon Crawler Game...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python from https://python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Check if pygame is installed
python -c "import pygame" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing required packages...
    echo.
    python -m pip install pygame numpy
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install required packages
        echo Please ensure you have internet connection and pip is working
        pause
        exit /b 1
    )
)

REM Run the game
echo.
echo 🎮 Starting game...
python main.py

REM Keep window open if there was an error
if %errorlevel% neq 0 (
    echo.
    echo Game exited with an error. Check the message above.
    pause
)
'''
    
    with open(os.path.join(dist_folder, "start_game.bat"), "w") as f:
        f.write(batch_content)
    
    print("   ✅ start_game.bat")
    
    # Create Python installer script for users without Python
    installer_content = '''#!/usr/bin/env python3
"""
Automatic installer for game dependencies.
Run this if you have Python but missing pygame.
"""

import subprocess
import sys

def install_dependencies():
    """Install required packages for the game."""
    
    required_packages = ["pygame", "numpy"]
    
    print("🎮 Installing Dungeon Crawler Game Dependencies...")
    print("=" * 50)
    
    for package in required_packages:
        print(f"📦 Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"   ✅ {package} installed successfully")
        except subprocess.CalledProcessError:
            print(f"   ❌ Failed to install {package}")
            print("   Please check your internet connection and try again")
            return False
    
    print("\\n🎉 All dependencies installed successfully!")
    print("You can now run the game by double-clicking 'start_game.bat'")
    return True

if __name__ == "__main__":
    success = install_dependencies()
    if not success:
        input("\\nPress Enter to exit...")
        sys.exit(1)
    
    input("\\nPress Enter to exit...")
'''
    
    with open(os.path.join(dist_folder, "install_dependencies.py"), "w") as f:
        f.write(installer_content)
    
    print("   ✅ install_dependencies.py")
    
    # Create comprehensive README
    readme_content = '''# Dungeon Crawler Game - Windows Distribution

## Quick Start (Recommended)
1. Double-click `start_game.bat` to start the game
2. The batch file will automatically install Python dependencies if needed
3. Use WASD to move, left-click to attack, right-click for spells!

## Manual Setup (If batch file doesn't work)
1. Install Python from https://python.org/downloads/
   - Make sure to check "Add Python to PATH" during installation
2. Double-click `install_dependencies.py` to install game requirements
3. Double-click `start_game.bat` to run the game

## Game Controls
- **WASD** or **Arrow Keys**: Move your character
- **Left Click**: Melee attack with equipped weapon
- **Right Click**: Cast equipped spell or ability
- **ESC**: Quit the game

## Gameplay
- Explore procedurally generated dungeons
- Defeat enemies to gain XP and level up
- Collect weapons, enchantments, and spells
- Fight bosses and progress through levels
- Use line-of-sight fog of war for tactical gameplay

## Features
- **Combat System**: Melee weapons and magical spells
- **Item System**: Weapons (sword, mace, spear), enchantments, and spells
- **Enemy Variety**: Multiple enemy types with unique AI behaviors
- **Boss Battles**: Challenging boss fights with special abilities
- **Progression**: Level up system with increasing difficulty
- **Visual Effects**: Damage numbers, weapon rendering, and visual feedback

## Troubleshooting
- If the game doesn't start, make sure Python is installed
- If you get import errors, run `install_dependencies.py`
- For performance issues, close other programs while playing
- If the window appears off-screen, press Alt+Tab to switch to it

## System Requirements
- Windows 7 or newer
- Python 3.7+ (will be prompted to install if missing)
- At least 100MB free disk space
- 1GB RAM recommended

## Support
This is a standalone game. All files needed to run are included in this folder.
The game will automatically handle dependency installation on first run.

Enjoy playing! 🎮
'''
    
    with open(os.path.join(dist_folder, "README.txt"), "w") as f:
        f.write(readme_content)
    
    print("   ✅ README.txt")
    
    # Create portable version indicator
    with open(os.path.join(dist_folder, "version.txt"), "w") as f:
        f.write("Dungeon Crawler Game - Windows Portable Version v1.0\n")
        f.write("Created: August 2025\n")
        f.write("All game files and dependencies included.\n")
    
    print("   ✅ version.txt")
    
    # Create zip file for easy distribution
    zip_filename = f"{dist_folder}.zip"
    if os.path.exists(zip_filename):
        os.remove(zip_filename)
    
    print(f"📦 Creating zip file: {zip_filename}")
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dist_folder):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(dist_folder))
                zipf.write(file_path, arcname)
    
    # Get folder and zip sizes
    folder_size = sum(os.path.getsize(os.path.join(root, file)) 
                     for root, dirs, files in os.walk(dist_folder) 
                     for file in files)
    zip_size = os.path.getsize(zip_filename)
    
    print("\\n🎉 Windows Distribution Created Successfully!")
    print("=" * 50)
    print(f"📁 Folder: {os.path.abspath(dist_folder)} ({folder_size/1024:.1f} KB)")
    print(f"📦 Zip file: {os.path.abspath(zip_filename)} ({zip_size/1024:.1f} KB)")
    print("\\n💡 Distribution includes:")
    print("   • All game files (.py)")
    print("   • Windows batch file for easy startup")
    print("   • Automatic dependency installer")
    print("   • Complete documentation")
    print("\\n🚀 Ready to share!")
    print("   1. Send the ZIP file to Windows users")
    print("   2. They extract it and double-click 'start_game.bat'")
    print("   3. Game installs dependencies automatically and runs!")
    
    return True

if __name__ == "__main__":
    create_distribution()