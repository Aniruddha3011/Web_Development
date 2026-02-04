@echo off
echo ========================================
echo Starting Universal Sentiment Analysis Platform
echo ========================================
echo.

echo Checking if dependencies are installed...
python -c "import flask" 2>nul
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Flask not installed!
    echo Please run: install_simple.bat
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Server starting at http://localhost:5000
echo ========================================
echo.
echo Open your browser and go to:
echo   http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
