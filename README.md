# Bot Polymarket Trading

## 🎯 Objectif
Bot de trading automatique sur Polymarket avec 10€ de capital test.
Apprentissage et amélioration continue basée sur les performances.

## 📁 Structure

```
bot-polymarket/
├── config.json           # Configuration & stratégies actives
├── strategies/
│   ├── arbitrage.py      # Arbitrage de prix entre marchés
│   ├── momentum.py       # Suivi des tendances
│   ├── value_bet.py      # Paris sur valeurs sous-cotées
│   └── whale_copy.py     # Copie des gros joueurs
├── core/
│   ├── risk_manager.py   # Gestion des risques (stop-loss, sizing)
│   ├── executor.py       # Exécution des ordres
│   ├── logger.py         # Journal des trades
│   └── analyzer.py       # Analyse post-trade
├── data/
│   ├── trades.json       # Historique des trades
│   └── performance.csv   # Métriques de performance
└── bot.py                # Orchestrateur principal
```

## 🧠 Stratégies Initiales (v1.0)

### 1️⃣ Arbitrage Simple
- **Description** : Même événement sur différents marchés avec écarts de prix
- **Signal** : Écart > 5% entre deux marchés identiques/similaires
- **Position** : Achat du moins cher, vente du plus cher
- **Hold time** : Quelques heures à quelques jours

### 2️⃣ Mean Reversion
- **Description** : Prix dévié fortement de la moyenne revient à la normale
- **Signal** : Prix < 20¢ ou > 80¢ sur marché à faible volatilité
- **Position** : Contre la tendance extrême
- **Hold time** : 1-7 jours

### 3️⃣ Copy Whales (Conservateur)
- **Description** : Suivre les gros joueurs avec historique positif
- **Signal** : Whale avec >70% win rate place >$1000
- **Position** : Même direction, taille proportionnelle
- **Hold time** : Suivre la position du whale

## ⚙️ Risk Management (Strict)

| Paramètre | Valeur | Rationale |
|-----------|--------|-----------|
| **Capital max** | $10 (10€) | Limite de test définie |
| **Max par trade** | $2 | 20% du capital (diversification) |
| **Stop-loss** | -30% | Coupe les positions perdantes |
| **Max positions ouvertes** | 3 | Évite sur-exposition |
| **Max trades/jour** | 2 | Évite over-trading |
| **Slippage max** | 2% | Accepte pas si écart trop grand |

## 📊 Métriques à Tracker

- Win rate (%)
- Profit moyen par trade
- Drawdown max
- Sharpe ratio
- Temps moyen de position
- Meilleure/pire stratégie

## 🔄 Boucle d'Amélioration

1. **Trade** (bot exécute)
2. **Log** (enregistre tout)
3. **Analyze** (analyse performance)
4. **Adjust** (ajuste stratégies)
5. **Repeat**

## 📝 Notes

- Commencer en **paper trading** 1 semaine
- Puis **live** avec 10€ si win rate > 55%
- Review hebdomadaire obligatoire
- Kill switch toujours accessible
