@echo off
echo ==============================================
echo       MediSecure-AI GitHub Push Helper
echo ==============================================
echo.
echo Current Git remote origin:
git remote -v
echo.
echo Checking git status...
git status
echo.

set /p CHOICE="Do you want to stage all changes and push to GitHub? (Y/N): "
if /i "%CHOICE%" neq "Y" (
    echo Operation cancelled by user.
    pause
    exit /b
)

echo.
echo Staging files...
git add .

set /p COMMIT_MSG="Enter commit message (leave blank for 'Initial push to Jashwanth1827/MediSecure-AI'): "
if "%COMMIT_MSG%"=="" set COMMIT_MSG=Initial push to Jashwanth1827/MediSecure-AI

echo.
echo Committing changes...
git commit -m "%COMMIT_MSG%"

echo.
echo Pushing changes to remote main branch...
git push -u origin main

if %ERRORLEVEL% equ 0 (
    echo.
    echo ==============================================
    echo  SUCCESS: Code pushed to GitHub successfully!
    echo ==============================================
) else (
    echo.
    echo ==============================================
    echo  ERROR: Failed to push to GitHub.
    echo  Please ensure the repository Jashwanth1827/MediSecure-AI
    echo  exists and you have proper credentials/access.
    echo ==============================================
)
echo.
pause
