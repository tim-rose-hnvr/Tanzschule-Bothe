@echo off
REM Startet die Marktanalyse lokal. Windows.
cd /d "%~dp0"
where py >nul 2>nul && (py serve.py %* & goto :eof)
where python >nul 2>nul && (python serve.py %* & goto :eof)
echo Python wurde nicht gefunden. Bitte Python 3 installieren: https://www.python.org/downloads/
pause
