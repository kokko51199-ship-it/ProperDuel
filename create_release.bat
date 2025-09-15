@echo off
setlocal enabledelayedexpansion

echo Creating Proper Duel Release Package...
echo.

REM Set version and package name
set VERSION=1.0
set PACKAGE_NAME=ProperDuel_v%VERSION%

REM Create release directory
if exist "release" rmdir /s /q "release"
mkdir "release"
mkdir "release\%PACKAGE_NAME%"

REM Check if executable exists
if not exist "dist\ProperDuel.exe" (
    echo ERROR: ProperDuel.exe not found in dist folder!
    echo Please build the game first using build_game.bat
    echo.
    pause
    exit /b 1
)

echo Copying files to release package...

REM Copy executable and documentation
copy "dist\ProperDuel.exe" "release\%PACKAGE_NAME%\"
copy "dist\README.txt" "release\%PACKAGE_NAME%\"

REM Create additional files for release
echo Creating version info...
echo Proper Duel v%VERSION% > "release\%PACKAGE_NAME%\VERSION.txt"
echo Built on %DATE% at %TIME% >> "release\%PACKAGE_NAME%\VERSION.txt"

echo Creating release notes...
(
echo # Proper Duel v%VERSION% - Release Notes
echo.
echo ## New Features
echo - Retro-style samurai fighting game
echo - Cinematic VIC VEGA splash screen with ASCII art
echo - Neon-styled main menu with atmospheric music
echo - Smooth 2D fighting mechanics
echo - Pixel art character animations
echo - Sound effects and background music
echo.
echo ## Technical Details
echo - Single executable file ^(no installation required^)
echo - Compatible with Windows 10/11 ^(64-bit^)
echo - File size: ~155 MB
echo - Built with Python + Pygame
echo.
echo ## Known Issues
echo - None reported
echo.
echo ## Credits
echo - Engine: Python + Pygame
echo - Art Style: 16x16 pixel art
echo - Music: Original soundtrack
) > "release\%PACKAGE_NAME%\RELEASE_NOTES.txt"

echo.
echo Creating ZIP archive...

REM Create ZIP file using PowerShell
powershell -command "Compress-Archive -Path 'release\%PACKAGE_NAME%' -DestinationPath 'release\%PACKAGE_NAME%.zip' -Force"

if exist "release\%PACKAGE_NAME%.zip" (
    echo.
    echo ============================================
    echo RELEASE PACKAGE CREATED SUCCESSFULLY!
    echo ============================================
    echo.
    echo Package: release\%PACKAGE_NAME%.zip
    echo.
    echo Contents:
    echo - ProperDuel.exe ^(Game executable^)
    echo - README.txt ^(User guide^)
    echo - VERSION.txt ^(Version information^)
    echo - RELEASE_NOTES.txt ^(Release notes^)
    echo.
    echo The game is ready for distribution!
    echo ============================================
) else (
    echo.
    echo ERROR: Failed to create ZIP archive!
)

echo.
echo Press any key to continue...
pause >nul