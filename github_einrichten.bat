@echo off
REM Legt das GitHub-Repository an und laedt den Quellcode hoch.
REM Voraussetzung: Git und die GitHub CLI (winget install --id GitHub.cli)
cd /d "%~dp0"
where gh >nul 2>nul || (echo Die GitHub CLI fehlt. Installiere sie mit: winget install --id GitHub.cli & pause & exit /b 1)
gh auth status >nul 2>nul || gh auth login
if not exist .git git init -b main
git add .
git commit -m "Studien-Dashboard: Prototyp der Finalisierungsphase"
gh repo create studien-dashboard --public --source=. --remote=origin --description "Studien-Dashboard: Portfolio im Kurs DLBDSOOFPP01_D, IU Internationale Hochschule" --push
gh repo view NyFY/studien-dashboard --json visibility,url
echo.
echo Fertig. Oeffne die Adresse einmal in einem privaten Fenster.
pause
