@echo off
setlocal

cd /d "%~dp0"

echo ========================================
echo LYRx Production Build - Python 3.11
echo ========================================
echo.

set "PY311=C:\Users\user\AppData\Local\Programs\Python\Python311\python.exe"

if not exist "%PY311%" (
    echo.
    echo ERROR: Python 3.11 was not found at:
    echo %PY311%
    echo.
    pause
    exit /b 1
)

if not exist ".env" (
    echo.
    echo ERROR: .env file was not found.
    echo.
    echo The local .env is required ONLY during
    echo the production build.
    echo.
    echo It will NOT be bundled into the EXE.
    echo.
    pause
    exit /b 1
)

if not exist "assets\icons\logo\LYRx.ico" (
    echo.
    echo ERROR: Proper LYRx.ico was not found.
    echo.
    echo Put your converted ICO file here:
    echo assets\icons\logo\LYRx.ico
    echo.
    pause
    exit /b 1
)


echo.
echo [1/5] Cleaning previous build...
echo.

if exist build (
    rmdir /s /q build
)

if exist dist (
    rmdir /s /q dist
)


echo.
echo [2/5] Preparing Firebase runtime configuration...
echo.

"%PY311%" -c "from dotenv import dotenv_values; from pathlib import Path; value=dotenv_values('.env').get('FIREBASE_API_KEY',''); assert value, 'FIREBASE_API_KEY is missing from .env'; Path('src/services/auth/_runtime_config.py').write_text('FIREBASE_API_KEY = ' + repr(str(value).strip()) + '\n', encoding='utf-8')"

if errorlevel 1 (
    echo.
    echo ERROR: FIREBASE_API_KEY could not be loaded from .env.
    echo.
    echo Please check your .env file.
    echo.
    pause
    exit /b 1
)

echo Firebase runtime configuration prepared.


echo.
echo [3/5] Building standalone LYRx.exe...
echo.

"%PY311%" -m PyInstaller --clean --noconfirm LYRx.spec

if errorlevel 1 (
    echo.
    echo ========================================
    echo BUILD FAILED
    echo ========================================
    echo.

    echo Removing temporary runtime configuration...

    if exist "src\services\auth\_runtime_config.py" (
        del /q "src\services\auth\_runtime_config.py"
    )

    echo.
    pause
    exit /b 1
)


echo.
echo [4/5] Removing temporary runtime configuration...
echo.

if exist "src\services\auth\_runtime_config.py" (
    del /q "src\services\auth\_runtime_config.py"
)


echo.
echo [5/5] Verifying production EXE...
echo.

if not exist "dist\LYRx.exe" (
    echo.
    echo ========================================
    echo ERROR
    echo ========================================
    echo.
    echo dist\LYRx.exe was not created.
    echo.
    pause
    exit /b 1
)


echo.
echo ========================================
echo BUILD SUCCESSFUL
echo ========================================
echo.
echo Production EXE:
echo.
echo dist\LYRx.exe
echo.
echo ========================================
echo.
echo IMPORTANT:
echo.
echo The production EXE does NOT require .env
echo on the user's computer.
echo.
echo You can copy ONLY:
echo.
echo LYRx.exe
echo.
echo to another Windows PC.
echo.
echo ========================================

pause

endlocal