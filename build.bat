@echo off
setlocal EnableExtensions

echo ========================================
echo   Dong goi CheckTop Tool (Windows)
echo ========================================
echo.

cd /d "%~dp0"

python --version >nul 2>&1
if errorlevel 1 (
    echo [LOI] Khong tim thay Python. Hay cai Python 3.10+ va tick "Add to PATH".
    pause
    exit /b 1
)

if not exist "tools\chrome-win64\chrome.exe" (
    echo [LOI] Thieu thu muc tools\chrome-win64\chrome.exe
    echo Hay dat day du Chrome portable + chromedriver + extension trong thu muc tools\
    pause
    exit /b 1
)

echo [1/4] Cai dependencies build...
python -m pip install --upgrade pip
python -m pip install pyinstaller PyQt5 PyQtWebEngine pymongo python-dotenv requests beautifulsoup4 selenium webdriver-manager gspread oauth2client

echo.
echo [2/4] Build file .exe bang PyInstaller...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

pyinstaller ^
  --name CheckTop ^
  --windowed ^
  --noconfirm ^
  --clean ^
  --icon logo1.ico ^
  --add-data "logo.png;." ^
  --add-data "logo1.png;." ^
  --add-data "logo1.ico;." ^
  --collect-all PyQt5.QtWebEngine ^
  --hidden-import pymongo ^
  --hidden-import bs4 ^
  --hidden-import gspread ^
  --hidden-import oauth2client ^
  --hidden-import oauth2client.service_account ^
  main.py

if errorlevel 1 (
    echo [LOI] PyInstaller build that bai.
    pause
    exit /b 1
)

echo.
echo [3/4] Copy Chrome, extension, logo vao thu muc phan phoi...
xcopy /E /I /Y /Q tools "dist\CheckTop\tools" >nul
copy /Y logo.png "dist\CheckTop\logo.png" >nul
copy /Y logo1.png "dist\CheckTop\logo1.png" >nul
copy /Y logo1.ico "dist\CheckTop\logo1.ico" >nul

echo.
echo [4/4] Hoan tat!
echo.
echo San pham nam tai:
echo   %cd%\dist\CheckTop\
echo.
echo File chay chinh:
echo   dist\CheckTop\CheckTop.exe
echo.
echo Luu y:
echo - Chay package_release.bat de tao file ZIP cho nguoi tai ve.
echo - Zip nam trong thu muc releases\
echo - Nguoi dung giai nen va chay CheckTop.exe (khong xoa thu muc tools).
echo - Can ket noi Internet de dang nhap MongoDB.
echo.
pause
