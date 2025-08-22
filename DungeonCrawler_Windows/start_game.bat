@echo off
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
