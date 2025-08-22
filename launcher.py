#!/usr/bin/env python3
"""
Dungeon Crawler Game Launcher
Entry point for PyInstaller executable
"""

import sys
import os

# Add game_src to Python path
game_src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'game_src')
if game_src_path not in sys.path:
    sys.path.insert(0, game_src_path)

# Import and run the game
if __name__ == '__main__':
    from game_src.main import main
    main()