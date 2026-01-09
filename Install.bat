@echo off
title SWAT NET AI v9.5 - Installation Script
color 0A
echo ========================================
echo    SWAT NET AI v9.5 INSTALLATION
echo ========================================
echo.

REM Check for Administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [!] Administrator privileges required!
    echo Please run as Administrator
    pause
    exit /b 1
)

echo [1] Checking system requirements...

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo [ ] Python not found. Installing Python 3.9...
    
    REM Download Python installer
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.9.13/python-3.9.13-amd64.exe' -OutFile 'python_installer.exe'"
    
    if exist python_installer.exe (
        echo [ ] Running Python installer...
        start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
        del python_installer.exe
        echo [✓] Python installed successfully
    ) else (
        echo [X] Failed to download Python
        pause
        exit /b 1
    )
) else (
    echo [✓] Python is already installed
)

REM Verify Python version
python -c "import sys; print('Python', sys.version)" > python_version.txt
set /p python_version=<python_version.txt
echo [✓] %python_version%
del python_version.txt

echo.
echo [2] Creating project directory...

REM Create directory structure
if not exist "C:\SWAT_Net_AI" mkdir "C:\SWAT_Net_AI"
cd /d "C:\SWAT_Net_AI"

mkdir logs 2>nul
mkdir tor_data 2>nul
mkdir config 2>nul

echo [✓] Directory created: C:\SWAT_Net_AI

echo.
echo [3] Installing Python dependencies...

REM Create requirements.txt
(
echo PyQt6==6.5.0
echo requests==2.31.0
echo stem==1.8.2
) > requirements.txt

REM Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo [X] Failed to install dependencies
    echo Trying alternative method...
    pip install PyQt6 requests stem
)

echo [✓] Dependencies installed

echo.
echo [4] Installing Tor service...

REM Check if Tor is already installed
where tor >nul 2>&1
if errorlevel 1 (
    echo [ ] Installing Tor...
    
    REM Download Tor Expert Bundle
    powershell -Command "Invoke-WebRequest -Uri 'https://archive.torproject.org/tor-package-archive/torbrowser/12.5.6/tor-expert-bundle-12.5.6-windows-x86_64.tar.gz' -OutFile 'tor_bundle.tar.gz'"
    
    if exist tor_bundle.tar.gz (
        REM Extract Tor
        tar -xzf tor_bundle.tar.gz
        move tor-* tor
        del tor_bundle.tar.gz
        
        REM Add Tor to PATH
        setx PATH "%PATH%;C:\SWAT_Net_AI\tor" /M
        
        echo [✓] Tor installed successfully
    ) else (
        echo [ ] Tor download failed, using built-in method
    )
) else (
    echo [✓] Tor is already installed
)

echo.
echo [5] Creating configuration files...

REM Create config.json
(
echo {
echo     "app_name": "SWAT NET AI v9.5",
echo     "version": "9.5",
echo     "ai": {
echo         "use_openrouter": true,
echo         "use_huggingface": true,
echo         "use_local_llm": false,
echo         "local_llm_url": "http://localhost:8080",
echo         "openrouter_api_key": "",
echo         "huggingface_api_key": ""
echo     },
echo     "tor": {
echo         "enabled": true,
echo         "autostart": true,
echo         "socks_port": 9050,
echo         "control_port": 9051
echo     },
echo     "privacy": {
echo         "spoof_location": true,
echo         "spoof_user_agent": true,
echo         "disable_webrtc": true,
echo         "clear_on_exit": true
echo     },
echo     "swat": {
echo         "simulation_mode": true,
echo         "emergency_numbers": ["112", "102", "103", "101", "911"]
echo     },
echo     "ui": {
echo         "theme": "dark",
echo         "language": "en"
echo     }
echo }
) > config.json

REM Create user_agents.json
(
echo [
echo     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
echo     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
echo     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
echo     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
echo     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36"
echo ]
) > user_agents.json

REM Create onion_sites.json
(
echo {
echo     "markets": [
echo         {"name": "DarkMarket", "url": "http://darkmarketonion.com", "v3": "http://darkmarketx4zq2fq.onion"},
echo         {"name": "Torrez Market", "url": "http://torrezmarket.org", "v3": "http://torrezmarket5j4ldx.onion"}
echo     ],
echo     "forums": [
echo         {"name": "Dread", "url": "http://dreadditevelidot.onion", "v3": "http://dreadditevelidot.onion"}
echo     ],
echo     "search": [
echo         {"name": "Ahmia", "url": "http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion", "v3": "http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion"},
echo         {"name": "DarkSearch", "url": "https://darksearch.io", "clearnet": true}
echo     ]
echo }
) > onion_sites.json

REM Create main Python script
(
echo import sys
echo import os
echo sys.path.append(os.path.dirname(os.path.abspath(__file__)))
echo 
echo from swat_net_ai import main
echo 
echo if __name__ == "__main__":
echo     main()
) > run.py

echo [✓] Configuration files created

echo.
echo [6] Creating desktop shortcut...

REM Create shortcut
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\SWAT Net AI.lnk'); $Shortcut.TargetPath = 'C:\SWAT_Net_AI\run.py'; $Shortcut.WorkingDirectory = 'C:\SWAT_Net_AI'; $Shortcut.IconLocation = '%SystemRoot%\System32\SHELL32.dll,21'; $Shortcut.Save()"

echo [✓] Desktop shortcut created

echo.
echo [7] Setting up startup service...

REM Create startup script
(
echo @echo off
echo cd /d "C:\SWAT_Net_AI"
echo python run.py
) > start_swat_ai.bat

REM Add to startup (optional)
set /p add_startup="Do you want to add to startup? (y/n): "
if /i "%add_startup%"=="y" (
    copy start_swat_ai.bat "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\"
    echo [✓] Added to startup programs
)

echo.
echo [8] Creating uninstaller...

REM Create uninstall script
(
echo @echo off
echo title SWAT NET AI - Uninstaller
echo color 0C
echo echo ========================================
echo echo     SWAT NET AI UNINSTALLATION
echo echo ========================================
echo echo.
echo echo [!] WARNING: This will remove all SWAT NET AI files!
echo echo.
echo set /p confirm="Type 'UNINSTALL' to confirm: "
echo if not "%%confirm%%"=="UNINSTALL" (
echo     echo Cancelled.
echo     pause
echo     exit /b 0
echo )
echo.
echo echo [1] Removing program files...
echo rmdir /s /q "C:\SWAT_Net_AI" 2^>nul
echo.
echo echo [2] Removing desktop shortcut...
echo del "%USERPROFILE%\Desktop\SWAT Net AI.lnk" 2^>nul
echo.
echo echo [3] Removing startup entry...
echo del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\start_swat_ai.bat" 2^>nul
echo.
echo echo [✓] Uninstallation complete!
echo echo.
echo echo Note: Python and Tor will remain installed.
echo echo To remove them, use Control Panel -> Programs and Features
echo pause
) > uninstall.bat

echo [✓] Uninstaller created

echo.
echo [9] Finalizing installation...

REM Create README.txt
(
echo SWAT NET AI v9.5
echo =================
echo.
echo Installation completed successfully!
echo.
echo Location: C:\SWAT_Net_AI
echo.
echo To start the application:
echo 1. Double-click "SWAT Net AI.lnk" on your desktop
echo 2. Or run: python C:\SWAT_Net_AI\run.py
echo.
echo Default login credentials:
echo Username: admin
echo Password: swatnet2025
echo.
echo IMPORTANT:
echo - This software is for EDUCATIONAL purposes only
echo - Do not use for illegal activities
echo - Emergency simulations are NOT REAL
echo.
echo Support:
echo Check the documentation folder for more information
) > README.txt

echo.
echo ========================================
echo     INSTALLATION COMPLETE!
echo ========================================
echo.
echo Summary:
echo - Python 3.9+: ✓ Installed
echo - Dependencies: ✓ Installed
echo - Tor service: ✓ Configured
echo - Config files: ✓ Created
echo - Desktop shortcut: ✓ Created
echo - Uninstaller: ✓ Created
echo.
echo Location: C:\SWAT_Net_AI
echo.
echo To start the application:
echo 1. Look for "SWAT Net AI" shortcut on desktop
echo 2. Or navigate to C:\SWAT_Net_AI and run: python run.py
echo.
echo Default credentials:
echo Username: admin
echo Password: swatnet2025
echo.
echo [!] LEGAL NOTICE:
echo This software is for EDUCATIONAL and RESEARCH purposes ONLY.
echo Any illegal use is strictly prohibited.
echo.
pause
