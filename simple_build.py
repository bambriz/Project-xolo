#!/usr/bin/env python3
"""
Simple executable builder for the game.
Creates a working Windows executable using basic PyInstaller options.
"""

import subprocess
import sys
import os
import shutil
import zipfile

def build_simple_exe():
    """Build executable with simple, reliable options."""
    
    print("🎮 Building Simple Windows Executable...")
    
    # Clean old builds
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    
    # Simple PyInstaller command that works reliably
    cmd = [
        'pyinstaller',
        '--onefile',           # Single file
        '--name=DungeonCrawler', # Executable name
        '--collect-all=pygame', # Include all pygame files
        '--collect-all=numpy',  # Include all numpy files
        'main.py'              # Main script
    ]
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ PyInstaller completed successfully!")
        
        # Find the executable (Linux creates without .exe extension)
        exe_files = []
        if os.path.exists('dist'):
            for file in os.listdir('dist'):
                if file.startswith('DungeonCrawler'):
                    exe_files.append(file)
        
        if exe_files:
            exe_file = exe_files[0]
            exe_path = f"dist/{exe_file}"
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            
            print(f"🎯 Created: {exe_path} ({size_mb:.1f} MB)")
            
            # Create distribution package
            dist_name = "DungeonCrawler_Windows_Game"
            if os.path.exists(dist_name):
                shutil.rmtree(dist_name)
            os.makedirs(dist_name)
            
            # Copy executable
            shutil.copy2(exe_path, f"{dist_name}/DungeonCrawler.exe")
            
            # Create simple instructions
            with open(f"{dist_name}/PLAY_GAME.txt", "w") as f:
                f.write("""DUNGEON CRAWLER GAME - WINDOWS VERSION

HOW TO PLAY:
1. Double-click "DungeonCrawler.exe" to start the game
2. Use WASD to move your character
3. Left-click to attack enemies
4. Right-click to cast spells
5. Collect items and level up!

NOTE: This game was built on Linux for Windows.
If it doesn't run, you may need to install:
- Microsoft Visual C++ Redistributable
- Or run the Python source version instead

CONTROLS:
- WASD/Arrows: Move
- Left Click: Melee attack
- Right Click: Cast spell
- ESC: Quit

ENJOY THE GAME! 🎮
""")
            
            # Create zip file
            zip_name = f"{dist_name}.zip"
            with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(dist_name):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_name = os.path.relpath(file_path, os.path.dirname(dist_name))
                        zipf.write(file_path, arc_name)
            
            zip_size = os.path.getsize(zip_name) / (1024 * 1024)
            
            print("\\n🎉 EXECUTABLE PACKAGE CREATED!")
            print("=" * 50)
            print(f"📦 ZIP: {zip_name} ({zip_size:.1f} MB)")
            print(f"🎮 Executable: {dist_name}/DungeonCrawler.exe")
            print("\\n✨ Ready to share with Windows users!")
            print("⚠️  Note: Cross-compiled from Linux, may need Visual C++ runtime")
            
            return True
        else:
            print("❌ No executable found after build")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

if __name__ == "__main__":
    if build_simple_exe():
        print("\\n🏆 Build successful!")
    else:
        print("\\n💥 Build failed!")