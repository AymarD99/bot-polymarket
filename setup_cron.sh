#!/bin/bash
# Setup du cron job pour Polymarket Bot

echo "🤖 Configuration du cron Polymarket Bot"
echo "========================================"

SCRIPT_PATH="/Users/aymarmichel/.openclaw/workspace/skills/bot-polymarket/cron_scan.sh"

# Vérifie si le script existe
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "❌ Script non trouvé: $SCRIPT_PATH"
    exit 1
fi

# Création du cron job
# Toutes les 30 minutes de 9h à 22h, du lundi au vendredi
CRON_JOB="*/30 9-22 * * 1-5 $SCRIPT_PATH"

# Supprime ancien cron si existe
crontab -l 2>/dev/null | grep -v "polymarket" | crontab -

# Ajoute nouveau cron
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "✅ Cron configuré:"
echo "   Fréquence: Toutes les 30 minutes"
echo "   Horaires: 9h00 - 22h00"
echo "   Jours: Lundi au Vendredi"
echo ""
echo "📊 Logs: ~/.openclaw/workspace/skills/bot-polymarket/data/cron.log"
echo ""
echo "📱 Pour recevoir les alerts sur Telegram:"
echo "   Configurer notification dans bot.py"
