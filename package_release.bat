@echo off
setlocal EnableExtensions

set VERSION=1.6
set APP_NAME=CheckTop
set RELEASE_DIR=releases
set ZIP_NAME=%APP_NAME%_v%VERSION%_Windows.zip

echo ========================================
echo   Tao file phat hanh cho nguoi tai ve
echo ========================================
echo.

cd /d "%~dp0"

if not exist "dist\%APP_NAME%\%APP_NAME%.exe" (
    echo [INFO] Chua co ban build. Dang chay build.bat...
    echo.
    call "%~dp0build.bat"
    if errorlevel 1 exit /b 1
)

if not exist "dist\%APP_NAME%\%APP_NAME%.exe" (
    echo [LOI] Khong tim thay dist\%APP_NAME%\%APP_NAME%.exe
    pause
    exit /b 1
)

echo [1/3] Copy huong dan cai dat vao goi phan phoi...
copy /Y "HUONG_DAN_CAI_DAT.txt" "dist\%APP_NAME%\HUONG_DAN_CAI_DAT.txt" >nul

echo [2/3] Tao thu muc releases...
if not exist "%RELEASE_DIR%" mkdir "%RELEASE_DIR%"

if exist "%RELEASE_DIR%\%ZIP_NAME%" del /f /q "%RELEASE_DIR%\%ZIP_NAME%"

echo [3/3] Nen thanh file ZIP (co the mat 1-2 phut)...
powershell -NoProfile -Command "Compress-Archive -Path 'dist\%APP_NAME%\*' -DestinationPath '%RELEASE_DIR%\%ZIP_NAME%' -Force"

if errorlevel 1 (
    echo [LOI] Khong tao duoc file ZIP.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   HOAN TAT!
echo ========================================
echo.
echo File nguoi dung tai ve:
echo   %cd%\%RELEASE_DIR%\%ZIP_NAME%
echo.
echo Cach phat hanh:
echo   1. Upload file ZIP len Google Drive / OneDrive / website
echo   2. Gui link tai ve cho khach hang
echo   3. Khach giai nen va chay CheckTop.exe
echo.
echo Goi y: dat mat khau ZIP hoac chi gui link cho nguoi da thanh toan.
echo.
pause
