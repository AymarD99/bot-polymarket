---
name: bot-polymarket
description: Bot de trading automatique sur Polymarket avec 10€ de capital test. Stratégies arbitrage, mean reversion, et copy whales. Mode paper trading pour test, puis live avec limites strictes.
version: 1.0.0
metadata:
  clawdbot:
    emoji: 🤖
    requires:
      env:
        - MATON_API_KEY
---

# Bot Polymarket Trading 🤖

Bot de trading automatique évolutif pour Polymarket avec capital limité (10€).

## 🎯 Objectifs

- 📊 Détecter opportunités sur Polymarket
- 💰 Trader automatiquement avec 10€ max
- 📈 Apprendre et s'améliorer au fil des trades
- 🛡️ Risk management strict

## 🧠 Stratégies (v1.0)

### 1️⃣ Arbitrage
Détecte écarts de prix >5% entre marchés similaires

### 2️⃣ Mean Reversion
Achète <20¢, vend >80¢ (retour à la moyenne)

### 3️⃣ Copy Whales (v1.1)
Suit les gros joueurs gagnants

## ⚙️ Risk Management

| Limite | Valeur |
|--------|--------|
| Capital max | $10 |
| Max/trade | $2 |
| Stop-loss | -30% |
| Max positions | 3 |
| Max trades/jour | 2 |

## 🚀 Utilisation

### Paper Trading (Test)
```bash
cd /Users/aymarmichel/.openclaw/workspace/skills/bot-polymarket
python3 bot.py
```

### Configurer
Modifier `config.json`:
- `"mode": "paper"` ou `"live"`
- `"capital"` selon ton budget
- Activer/désactiver stratégies

### Cron (Auto-scan)
```bash
# Toutes les 30 minutes pendant trading hours
python3 bot.py
```

## 📊 Fichiers

- `bot.py` - Orchestrateur principal
- `config.json` - Configuration
- `data/trades.json` - Historique trades
- `data/performance.csv` - Métriques
- `data/bot.log` - Logs détaillés

## 🔄 Amélioration Continue

1. Paper trading 1 semaine
2. Analyse des résultats
3. Ajustement stratégies
4. Live avec 10€
5. Itération hebdomadaire
