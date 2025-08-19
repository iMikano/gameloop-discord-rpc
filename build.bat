@echo off
echo Building Gameloop Discord Rich Presence...
echo.

echo Installing dependencies...
pip install psutil pypresence pillow pystray pyinstaller

if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "*.spec" del "*.spec"

echo Building executable...
pyinstaller --onefile ^
    --windowed ^
    --name "Gameloop-Discord-RPC" ^
    --exclude-module=matplotlib ^
    --exclude-module=numpy ^
    Gameloop-Discord-RPC.py

if exist "dist\Gameloop-Discord-RPC.exe" (
    echo.
    echo Build successful!
    echo.
    echo Executable created: dist\Gameloop-Discord-RPC.exe
) else (
    echo.
    echo Build failed!
    echo Make sure all dependencies are installed.
)

pause