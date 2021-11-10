@echo off
cd "%PROGRAMFILES(X86)%"\obs-studio\bin\64bit\
start obs64.exe --minimize-to-tray --disable-updater --startstreaming
cd %USERPROFILE%\Desktop\FumoCam\src\
echo [System Reboot Detected]> ..\output\main_process.txt
echo Please wait. Initializing core systems. (0/3)> ..\output\main_status.txt
TIMEOUT /T 15
start /wait initialize_serial.py
echo [System Reboot Detected]> ..\output\main_process.txt
echo Please wait. Initializing core systems. (1/3)> ..\output\main_status.txt
TIMEOUT /T 5
start temps.py
echo [System Reboot Detected]> ..\output\main_process.txt
echo Please wait. Initializing core systems. (2/3)> ..\output\main_status.txt
TIMEOUT /T 10
start main.py


