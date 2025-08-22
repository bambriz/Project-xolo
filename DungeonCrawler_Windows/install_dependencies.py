#!/usr/bin/env python3
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
    
    print("\n🎉 All dependencies installed successfully!")
    print("You can now run the game by double-clicking 'start_game.bat'")
    return True

if __name__ == "__main__":
    success = install_dependencies()
    if not success:
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    input("\nPress Enter to exit...")
