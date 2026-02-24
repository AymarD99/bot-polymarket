#!/bin/bash
# Polymarket Bot - Cron script pour scans automatiques
# Exécuté toutes les 30 minutes pendant les heures de trading

SCRIPT_DIR="/Users/aymarmichel/.openclaw/workspace/skills/bot-polymarket"
LOG_FILE="$SCRIPT_DIR/data/cron.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] Démarrage scan Polymarket..." >> "$LOG_FILE"

cd "$SCRIPT_DIR" || exit 1

# Exécute le bot et capture la sortie
python3 bot.py >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "[$DATE] ✅ Scan terminé avec succès" >> "$LOG_FILE"
else
    echo "[$DATE] ❌ Erreur scan (code: $EXIT_CODE)" >> "$LOG_FILE"
fi

echo "---" >> "$LOG_FILE"
