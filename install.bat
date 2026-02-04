@echo off
echo ========================================
echo Universal Sentiment Analysis Platform
echo Installation Script
echo ========================================
echo.

echo Checking virtual environment...
if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please create one first: python -m venv .venv
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
echo This may take a few minutes...
echo.

REM Try different methods to install packages
.venv\Scripts\python.exe -m pip install --upgrade pip 2>nul
if %errorlevel% neq 0 (
    echo Trying alternative installation method...
    .venv\Scripts\python -m pip install --upgrade pip
)

.venv\Scripts\python.exe -m pip install flask flask-cors vaderSentiment pandas beautifulsoup4 lxml matplotlib numpy 2>nul
if %errorlevel% neq 0 (
    echo Trying alternative installation method...
    .venv\Scripts\python -m pip install flask flask-cors vaderSentiment pandas beautifulsoup4 lxml matplotlib numpy
)

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo To run the application:
echo 1. Run: run.bat
echo    OR
echo 2. Run: .venv\Scripts\python app.py
echo.
echo Then open your browser to: http://localhost:5000
echo.
pause
