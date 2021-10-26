@echo off
cd "%PROGRAMFILES(X86)%"\obs-studio\bin\64bit\
start obs64.exe --minimize-to-tray --disable-updater --startstreaming
cd %USERPROFILE%\Desktop\FumoCam\src\
echo [System Reboot Detected]> ..\output\main_process.txt
echo Please wait. Initializing core systems.> ..\output\main_status.txt
start temps.py
TIMEOUT /T 20
start main.py


