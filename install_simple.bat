@echo off
echo ========================================
echo Universal Sentiment Analysis Platform
echo Simple Installation (No VirtualEnv)
echo ========================================
echo.

echo This will install packages to your system Python.
echo.
echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo Installing required packages...
echo This may take a few minutes...
echo.

python -m pip install --upgrade pip
python -m pip install flask flask-cors vaderSentiment pandas beautifulsoup4 lxml

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Installation failed!
    echo.
    echo Possible solutions:
    echo 1. Run this script as Administrator
    echo 2. Check if pip is installed: python -m pip --version
    echo 3. See INSTALL_HELP.md for more solutions
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo To run the application:
echo   python app.py
echo.
echo Then open your browser to: http://localhost:5000
echo.
pause
