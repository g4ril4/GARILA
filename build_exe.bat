@echo off
chcp 65001 > nul
title GARILA AI - Application Builder
echo ========================================================
echo   GARILA AI - Building Standalone Windows Application
echo ========================================================
echo.

echo [1/3] Checking PyInstaller...
python -m pip install --upgrade pyinstaller
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install PyInstaller. Please check internet connection.
    pause
    exit /b %errorlevel%
)

echo.
echo [2/3] Building GARILA.exe with logo.ico...
pyinstaller --noconfirm --clean GARILA.spec
if %errorlevel% neq 0 (
    echo [ERROR] Build failed! Check the log above.
    pause
    exit /b %errorlevel%
)

echo.
echo [3/3] Copying initial config to dist folder...
if not exist "dist\GARILA\config" mkdir "dist\GARILA\config"
copy /Y "config\api_keys.json" "dist\GARILA\config\api_keys.json" > nul
copy /Y "logo.ico" "dist\GARILA\" > nul

echo.
echo ========================================================
echo   SUCCESS! GARILA.exe has been built successfully!
echo   Location: dist\GARILA\GARILA.exe
echo ========================================================
echo.
pause
