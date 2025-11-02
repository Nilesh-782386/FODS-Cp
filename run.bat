@echo off
setlocal enabledelayedexpansion

echo.
echo ============================================================
echo   Algorithm Visualizer v6.0 - ZERO OVERLAPPING EDITION
echo ============================================================
echo.
echo New Features:
echo   ✓ Perfect Layout - NO Overlapping Panels
echo   ✓ GridSpec Layout System
echo   ✓ All Algorithms Included
echo   ✓ Enhanced Spacing and Margins
echo   ✓ Professional Appearance
echo ============================================================
echo.

cd /d "%~dp0"

REM Check if required files exist
if not exist "main.c" (
    echo [ERROR] main.c not found!
    echo Please ensure all files are in the same directory.
    pause
    exit /b 1
)

if not exist "visualize.py" (
    echo [ERROR] visualize.py not found!
    echo Please ensure all files are in the same directory.
    pause
    exit /b 1
)

REM Clean up old files
echo [STEP 1] Cleaning up previous files...
if exist "algorithm_steps.json" del "algorithm_steps.json"
if exist "algorithm_config.json" del "algorithm_config.json"
if exist "main.exe" del "main.exe"
echo ✓ Cleanup complete
echo.

REM Compile C program
echo [STEP 2] Compiling C program...
gcc -Wall -Wextra main.c -o main.exe
if errorlevel 1 (
    echo [ERROR] Compilation failed!
    echo.
    echo Troubleshooting:
    echo 1. Check if GCC is installed: gcc --version
    echo 2. Install MinGW-w64 if not installed
    echo 3. Add GCC to PATH environment variable
    pause
    exit /b 1
)

if not exist "main.exe" (
    echo [ERROR] Executable not created after compilation!
    pause
    exit /b 1
)
echo ✓ Compilation successful
echo.

REM Run algorithm selection
echo [STEP 3] Running algorithm generator...
echo ============================================================
echo.
echo Available Data Structures and Algorithms:
echo.
echo 1. Arrays (7 Algorithms)
echo    • Linear Search, Binary Search
echo    • Bubble Sort, Selection Sort, Insertion Sort
echo    • Quick Sort, Merge Sort
echo.
echo 2. Linked Lists (5 Operations)
echo    • Insert at Beginning/End/Sequential
echo    • Search, Multiple Operations Demo
echo.
echo 3. Stack - LIFO (3 Operations)
echo    • Push, Pop, Combined Demo
echo.
echo 4. Queue - FIFO (3 Operations)
echo    • Enqueue, Dequeue, Combined Demo
echo.
echo 5. Binary Search Tree (5 Operations)
echo    • Insert, Search, Delete
echo    • Inorder Traversal, Complete Demo
echo.
echo ============================================================
echo.
main.exe
if errorlevel 1 (
    echo.
    echo [ERROR] Algorithm execution failed!
    echo Please check your input and try again.
    pause
    exit /b 1
)

if not exist "algorithm_steps.json" (
    echo [ERROR] No visualization data generated!
    echo Please check your algorithm selection.
    pause
    exit /b 1
)

if not exist "algorithm_config.json" (
    echo [ERROR] No configuration file generated!
    pause
    exit /b 1
)
echo.
echo ✓ Algorithm data generated successfully
echo.

REM Check Python installation
echo [STEP 4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo.
    echo Please install Python 3.7+ from python.org
    echo Required packages: matplotlib, numpy
    echo Install with: pip install matplotlib numpy
    pause
    exit /b 1
)

REM Display Python version
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✓ Found: %PYTHON_VERSION%
echo.

REM Check required packages
echo [STEP 5] Verifying required packages...
python -c "import matplotlib" 2>nul
if errorlevel 1 (
    echo [WARNING] matplotlib not found!
    echo Installing matplotlib...
    pip install matplotlib --quiet
)

python -c "import numpy" 2>nul
if errorlevel 1 (
    echo [WARNING] numpy not found!
    echo Installing numpy...
    pip install numpy --quiet
)
echo ✓ All packages verified
echo.

REM Launch visualization
echo [STEP 6] Launching enhanced visualization...
echo ============================================================
echo.
echo Visualization Features:
echo   • ZERO OVERLAPPING LAYOUT
echo   • GridSpec Perfect Positioning
echo   • 6 Separate Information Panels
echo   • Interactive Learning Mode
echo   • Live Statistics Dashboard
echo   • Professional Code Display
echo   • Input Pattern Analysis
echo.
echo Controls:
echo   [Play/Pause] - Control animation
echo   [Reset]      - Restart from beginning
echo   [Back/Next]  - Step through manually
echo   [Learn]      - Toggle learning mode
echo   [Speed]      - Adjust animation speed
echo.
echo ============================================================
echo.

python visualize.py
if errorlevel 1 (
    echo.
    echo [ERROR] Visualization failed!
    echo.
    echo Troubleshooting:
    echo 1. Check if matplotlib and numpy are installed
    echo 2. Run: pip install matplotlib numpy --upgrade
    echo 3. Check Python version (requires 3.7+)
    echo 4. Verify JSON files were created correctly
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   Visualization completed successfully!
echo ============================================================
echo.
echo Thank you for using Algorithm Visualizer v6.0!
echo.
echo Files generated:
echo   • algorithm_steps.json  - Visualization data
echo   • algorithm_config.json - Configuration
echo   • main.exe              - Compiled program
echo.
echo To run again: Simply execute run.bat
echo.
pause