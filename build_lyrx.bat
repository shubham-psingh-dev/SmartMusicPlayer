@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo LYRx Production Build - Python 3.11
echo ========================================

set "PY311=C:\Users\user\AppData\Local\Programs\Python\Python311\python.exe"

if not exist "%PY311%" (
    echo.
    echo ERROR: Python 3.11 was not found at:
    echo %PY311%
    echo.
    pause
    exit /b 1
)

if not exist "assets\icons\logo\LYRx.ico" (
    echo.
    echo ERROR: Proper LYRx.ico was not found.
    echo Put your converted ICO file here:
    echo assets\icons\logo\LYRx.ico
    echo.
    pause
    exit /b 1
)

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

"%PY311%" -m PyInstaller --clean --noconfirm LYRx.spec

if errorlevel 1 (
    echo.
    echo BUILD FAILED.
    pause
    exit /b 1
)

echo.
echo ========================================
echo BUILD SUCCESSFUL
 echo ========================================
echo EXE: dist\LYRx.exe
 echo.
pause
endlocal
