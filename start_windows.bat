@echo off
REM Startet das Studien-Dashboard unter Windows per Doppelklick.
REM Das Konsolenfenster im Hintergrund gehoert dazu und darf offen bleiben.
cd /d "%~dp0"

REM Zuerst den Windows-Starter "py" versuchen, dann "python".
py main.py %*
if %errorlevel%==9009 goto versuchePython
if %errorlevel% neq 0 goto fehler
goto ende

:versuchePython
python main.py %*
if %errorlevel% neq 0 goto fehler
goto ende

:fehler
echo.
echo Das Programm wurde mit einem Fehler beendet.
echo Ist Python 3.10 oder neuer installiert und im PATH eingetragen?
pause

:ende
