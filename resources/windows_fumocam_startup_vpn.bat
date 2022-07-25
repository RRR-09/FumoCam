@echo off
echo [System Reboot Detected]> ..\output\main_process.txt
echo Obscuring digital footprint... > ..\output\main_status.txt
::Start VPN
cd "%PROGRAMFILES%"\NordVPN
start NordVPN.exe
TIMEOUT /T 35

::Start OBS
cd "%PROGRAMFILES(X86)%"\obs-studio\bin\64bit\
start obs64.exe --minimize-to-tray --disable-updater --startstreaming
cd %USERPROFILE%\Desktop\FumoCam\src\
echo Digital footprint successfully obscured, live stream established. > ..\output\main_status.txt" 
echo Please wait. Initializing core systems. (0/3) >> ..\output\main_status.txt" 
TIMEOUT /T 15

::Initialize Serial Connection
start /wait initialize_serial.py
echo [System Reboot Detected]> ..\output\main_process.txt
echo Digital footprint successfully obscured, live stream established. > ..\output\main_status.txt" 
echo Please wait. Initializing core systems. (1/3) >> ..\output\main_status.txt" 
TIMEOUT /T 5

::Initialize Monitoring
start poetry run python temps.py
echo [System Reboot Detected]> ..\output\main_process.txt
echo Digital footprint successfully obscured, live stream established. > ..\output\main_status.txt" 
echo Please wait. Initializing core systems. (2/3) >> ..\output\main_status.txt" 
TIMEOUT /T 10

::Initialize Main Program
start poetry run python main.py


