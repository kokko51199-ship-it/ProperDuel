#!/usr/bin/env python3
"""
Build script for creating Proper Duel executable
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def main():
    """Build the executable using PyInstaller."""
    print("Building Proper Duel executable...")
    
    # Clean previous builds
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",                    # Single executable file
        "--windowed",                   # No console window (for GUI apps)
        "--name=ProperDuel",           # Name of the executable
        "--add-data=assets;assets",    # Include assets folder
        "--add-data=game;game",        # Include game modules
        "--hidden-import=pygame",      # Ensure pygame is included
        "--hidden-import=pygame.mixer", # Ensure pygame.mixer is included
        "--icon=assets/icon.ico",      # Game icon (if exists)
        "main.py"                      # Main script
    ]
    
    # Remove icon parameter if icon doesn't exist
    if not os.path.exists("assets/icon.ico"):
        cmd = [arg for arg in cmd if not arg.startswith("--icon")]
        print("Note: No icon.ico found, building without custom icon")
    
    try:
        # Run PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build successful!")
        print(f"Executable created: dist/ProperDuel.exe")
        
        # Check file size
        exe_path = Path("dist/ProperDuel.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"File size: {size_mb:.1f} MB")
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("PyInstaller not found. Please install it with: pip install pyinstaller")
        sys.exit(1)

if __name__ == "__main__":
    main()