#!/usr/bin/env bash
# Legt das GitHub-Repository an und laedt den Quellcode hoch.
#
# Aufruf aus diesem Ordner heraus:
#     bash github_einrichten.sh
#
# Voraussetzung ist die GitHub CLI (gh). Ist sie nicht installiert:
#     macOS:    brew install gh
#     Windows:  winget install --id GitHub.cli
# Danach einmalig anmelden mit:  gh auth login

set -euo pipefail

BENUTZER="NyFY"
REPO="studien-dashboard"
BESCHREIBUNG="Studien-Dashboard: Portfolio im Kurs DLBDSOOFPP01_D, IU Internationale Hochschule"

echo "== Studien-Dashboard nach GitHub =="

if ! command -v git >/dev/null 2>&1; then
    echo "FEHLER: git ist nicht installiert." >&2
    exit 1
fi
if ! command -v gh >/dev/null 2>&1; then
    echo "FEHLER: Die GitHub CLI (gh) ist nicht installiert." >&2
    echo "  macOS:   brew install gh" >&2
    echo "  Windows: winget install --id GitHub.cli" >&2
    exit 1
fi
if ! gh auth status >/dev/null 2>&1; then
    echo "Du bist noch nicht angemeldet. Es oeffnet sich gleich der Browser."
    gh auth login
fi

echo "-> lokales Repository vorbereiten"
if [ ! -d .git ]; then
    git init -b main
fi
git add .
if git diff --cached --quiet; then
    echo "   keine Aenderungen einzuchecken"
else
    git commit -m "Studien-Dashboard: Prototyp der Finalisierungsphase"
fi

echo "-> Repository auf GitHub anlegen und hochladen"
if gh repo view "$BENUTZER/$REPO" >/dev/null 2>&1; then
    echo "   Repository existiert bereits, es wird nur aktualisiert"
    git remote get-url origin >/dev/null 2>&1 || \
        git remote add origin "https://github.com/$BENUTZER/$REPO.git"
    git push -u origin main
else
    gh repo create "$REPO" --public --source=. --remote=origin \
        --description "$BESCHREIBUNG" --push
fi

echo "-> Sichtbarkeit pruefen"
gh repo view "$BENUTZER/$REPO" --json visibility,url \
    --jq '"   Sichtbarkeit: \(.visibility)\n   Adresse:      \(.url)"'

echo ""
echo "Fertig. Oeffne die Adresse einmal in einem privaten Fenster."
echo "Ist sie dort erreichbar, sieht sie auch deine Tutorin oder dein Tutor."
