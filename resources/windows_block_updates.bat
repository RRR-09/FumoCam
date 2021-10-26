@echo off
netsh advfirewall firewall add rule name="Block Updates" dir=out action=block program="%SystemRoot%\System32\svchost.exe" enable=yes protocol=TCP
pause