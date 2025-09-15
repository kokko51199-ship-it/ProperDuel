# Proper Duel - Build Instructions

## Creating the Executable

This document explains how to build the Proper Duel executable from source.

### Prerequisites
- Python 3.13+ installed
- PyInstaller package (`pip install pyinstaller`)
- All game dependencies installed (`pip install pygame`)

### Build Process

1. **Install PyInstaller:**
   ```
   pip install pyinstaller
   ```

2. **Run the build using the spec file:**
   ```
   pyinstaller ProperDuel.spec --noconfirm
   ```

3. **Alternative simple build:**
   ```
   python build_exe.py
   ```

### Asset Path Handling
The game uses a custom resource utility (`game/resource_utils.py`) to handle asset paths correctly in both development and PyInstaller environments:
- **Development:** Uses relative paths from project directory
- **PyInstaller:** Uses `sys._MEIPASS` temporary extraction directory
- **Functions:** `sprite_path()`, `audio_path()`, `asset_path()`, `get_resource_path()`

### Files Included in Build
- All Python game modules (`game/` directory)
- All assets (`assets/` directory including sprites and audio)
- PyGame libraries and dependencies
- Python runtime
- Resource path utilities for proper asset loading

### Build Configuration (ProperDuel.spec)
- **Type:** Single file executable (`--onefile`)
- **Mode:** Windowed application (`--windowed`)
- **Assets:** Automatically bundled via spec file functions
- **Hidden Imports:** PyGame modules explicitly included
- **Asset Handling:** Custom functions ensure proper path resolution

### Output
- **Executable:** `dist/ProperDuel.exe`
- **Size:** ~155 MB (includes Python runtime + PyGame + assets)
- **Dependencies:** None (standalone executable)
- **Asset Loading:** Works correctly in bundled environment

### Recent Fixes
- ✅ **Asset Path Resolution:** Fixed PyInstaller asset loading using `sys._MEIPASS`
- ✅ **Resource Utilities:** Added proper path handling for development vs bundled environments
- ✅ **Audio Loading:** All sound effects and music now load correctly in executable
- ✅ **Sprite Loading:** All character animations and backgrounds load properly
- ✅ **Scene Assets:** Splash screen, menu, and fight scenes fully functional

### Optimization Notes
- File size could be reduced by using `--onedir` instead of `--onefile`
- UPX compression is enabled by default
- Consider excluding unused Python modules for smaller builds

### Distribution
The `dist/` folder contains the complete distributable game:
- `ProperDuel.exe` - Main executable (fully functional with assets)
- `README.txt` - User documentation

### Testing
✅ Tested on Windows 10/11 - all assets load correctly
✅ Splash screen, menu music, and fight scenes work properly
✅ No asset path errors in bundled executable
Always test the executable on a clean system without Python installed to ensure all dependencies are properly bundled.