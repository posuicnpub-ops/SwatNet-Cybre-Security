# SwatNet-Cybre-Security

SWAT NET AI v9.5 - Complete Installation Guide
🚀 QUICK INSTALLATION
Step 1: Save this as install.bat
Step 2: Right-click → "Run as administrator"
Step 3: Follow the on-screen instructions

📦 WHAT GETS INSTALLED:
1. Python Environment
Python 3.9+ (if not installed)

Required libraries: PyQt6, requests, stem

Automatic PATH configuration

2. Tor Network
Tor Expert Bundle

Automatic proxy setup (127.0.0.1:9050)

Control port: 9051

3. Application Files
Main program: swat_net_ai.py

Configuration files

Desktop shortcut

Uninstaller

4. System Integration
Optional startup entry

Firewall rules

File associations

🔧 INSTALLATION LOCATION:
text
C:\SWAT_Net_AI\
├── swat_net_ai.py     (Main program)
├── run.py            (Launcher)
├── config.json       (Settings)
├── tor_data/         (Tor files)
├── logs/            (Application logs)
└── uninstall.bat    (Remove everything)
🎯 LAUNCH OPTIONS:
After installation:

Desktop: Double-click "SWAT Net AI.lnk"

Start Menu: Search "SWAT Net AI"

Command Line: python C:\SWAT_Net_AI\run.py

Default Login:

Username: admin

Password: swatnet2025

⚠️ IMPORTANT NOTES:
Legal Requirements:
✅ FOR EDUCATIONAL USE ONLY
✅ EMERGENCY SIMULATIONS ARE NOT REAL
✅ DARKNET ACCESS FOR RESEARCH ONLY
❌ NEVER USE FOR ILLEGAL ACTIVITIES

System Requirements:
Windows 7/8/10/11 (64-bit)

2GB RAM minimum

500MB free space

Internet for initial setup

🛠️ TROUBLESHOOTING:
Common Issues:
1. "Python not found"

Install Python manually from python.org

Check "Add Python to PATH" during install

2. Tor not connecting

Check if port 9050 is free: netstat -an | find "9050"

Restart Tor: taskkill /f /im tor.exe

3. Firewall blocking
Run as Admin:

cmd
netsh advfirewall firewall add rule name="SWAT AI" dir=out action=allow program="C:\SWAT_Net_AI\python.exe"
🔄 UPDATING:
Automatic: Application checks on startup
Manual: Run update.bat in installation folder

🗑️ UNINSTALLATION:
Complete Removal:

Run uninstall.bat in C:\SWAT_Net_AI

Type "UNINSTALL" to confirm

Removes all files and shortcuts

What stays:

Python (system-wide installation)

Tor (if installed separately)

📞 SUPPORT:
Included Tools:

diagnostics.py - System check

view_logs.py - Log viewer

test_network.py - Connection test

Getting Help:

Check README.txt in installation folder

View application logs in C:\SWAT_Net_AI\logs\

Run diagnostics for automated troubleshooting

⚡ ONE-LINE INSTALL (Advanced Users):
cmd
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/yourrepo/install.bat' -OutFile 'install.bat' && install.bat /silent /accepteula"
✅ VERIFICATION:
After installation, verify:

Desktop shortcut exists

Can launch application

Tor connection works (check status bar)

AI assistant responds

To verify Tor:

Open application

Go to Privacy tab

Click "Check Current IP"

Should show Tor IP address

🎮 QUICK START:
Launch the application

Login with admin/swatnet2025

Enable Tor in Privacy tab

Test AI in AI Chat tab

Explore tools in respective tabs

📋 POST-INSTALLATION CHECKLIST:
Application launches

Can login successfully

Tor connection established

AI responds to queries

All tabs accessible

No error messages

⚠️ FINAL WARNING:
THIS SOFTWARE IS FOR:

Education and research

Cybersecurity training

Privacy awareness

Ethical hacking practice

THIS SOFTWARE IS NOT FOR:

Illegal activities

Real emergency calls

Harassment or abuse

Criminal purposes

VIOLATORS WILL BE PROSECUTED TO THE FULLEST EXTENT OF THE LAW
