@echo off
echo Building Proper Duel executable...
echo.

REM Clean previous builds
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo Cleaned previous builds.
echo.

REM Build with PyInstaller
echo Building executable...
pyinstaller ProperDuel.spec --noconfirm

REM Check if build was successful
if exist "dist\ProperDuel.exe" (
    echo.
    echo ============================================
    echo BUILD SUCCESSFUL!
    echo ============================================
    echo.
    echo Executable created: dist\ProperDuel.exe
    
    REM Get file size
    for %%A in ("dist\ProperDuel.exe") do (
        set size=%%~zA
        set /a sizeMB=!size! / 1048576
    )
    echo File size: approximately !sizeMB! MB
    echo.
    echo The game is ready to distribute!
    echo ============================================
) else (
    echo.
    echo ============================================
    echo BUILD FAILED!
    echo ============================================
    echo Please check the error messages above.
)

echo.
echo Press any key to continue...
pause >nul