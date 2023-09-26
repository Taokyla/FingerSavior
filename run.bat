@ECHO OFF
REG QUERY "HKU\S-1-5-19">NUL 2>NUL&& GOTO :skip
powershell -Command "Start-Process '%~sdpnx0' -Verb RunAs"&&EXIT

:skip
cd /D "%~dp0"
py src/main.py