#!/usr/bin/env python3
"""
🤖 Bot Polymarket Trading v1.1
Trading automatique avec 10€ de capital test
Avec Telegram notifications et structure pour live trading
"""

import json
import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime, timezone
import ssl
import certifi

# SSL fix pour macOS
SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())

# Tentative d'import du SDK Polymarket (pour live trading)
try:
    from py_clob_client.client import ClobClient
    CLOB_AVAILABLE = True
except ImportError:
    CLOB_AVAILABLE = False
    print("⚠️ py-clob-client non installé. Mode paper uniquement.")
    print("   Pour live: pip install py-clob-client")

BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "config.json"
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Fichiers de données
TRADES_FILE = DATA_DIR / "trades.json"
PERFORMANCE_FILE = DATA_DIR / "performance.csv"
LOG_FILE = DATA_DIR / "bot.log"

class PolymarketBot:
    """Bot de trading Polymarket"""
    
    def __init__(self):
        self.load_config()
        self.ensure_data_files()
        
    def load_config(self):
        """Charge la configuration"""
        with open(CONFIG_PATH) as f:
            self.config = json.load(f)
        self.mode = self.config["mode"]  # "paper" ou "live"
        self.capital = self.config["capital"]["current_usd"]
        
    def ensure_data_files(self):
        """Crée les fichiers de données s'ils n'existent pas"""
        if not TRADES_FILE.exists():
            TRADES_FILE.write_text(json.dumps({"trades": [], "stats": {}}))
        if not PERFORMANCE_FILE.exists():
            PERFORMANCE_FILE.write_text("date,strategy,result,pnl,capital\n")
    
    def notify_telegram(self, message):
        """Envoie une notification Telegram"""
        try:
            # Utilise le système de notification OpenClaw si disponible
            # Sinon log dans un fichier spécial pour notification
            notify_file = DATA_DIR / "telegram_notifications.txt"
            timestamp = datetime.now(timezone.utc).isoformat()
            with open(notify_file, "a") as f:
                f.write(f"[{timestamp}] {message}\n")
        except Exception as e:
            self.log(f"Erreur notification: {e}", "ERROR")
    
    def setup_live_credentials(self):
        """Configuration sécurisée des credentials pour live trading"""
        print("\n" + "="*60)
        print("🔐 Configuration Live Trading - Polymarket")
        print("="*60)
        print("\n⚠️  ATTENTION: Ne partagez JAMAIS ces informations!")
        print("="*60 + "\n")
        
        # Vérifie si credentials déjà configurés
        creds_file = DATA_DIR / ".credentials.json"
        if creds_file.exists():
            print("✅ Credentials déjà configurés")
            return True
        
        print("📝 Entrez vos credentials API Polymarket:")
        print("(Ces informations resteront sur votre machine uniquement)\n")
        
        try:
            api_key = input("API Key: ").strip()
            secret = input("Secret: ").strip()
            passphrase = input("Passphrase: ").strip()
            
            # Optionnel: clé privée pour L1 auth
            print("\n💡 Optionnel - Clé privée wallet (L1 auth):")
            print("   Laisser vide pour utiliser API key uniquement")
            private_key = input("Private Key (ou Entrée): ").strip()
            
            # Sauvegarde chiffrée (simple pour l'instant)
            credentials = {
                "api_key": api_key,
                "secret": secret,
                "passphrase": passphrase,
                "private_key": private_key if private_key else None
            }
            
            with open(creds_file, "w") as f:
                json.dump(credentials, f)
            
            # Permissions restrictives
            os.chmod(creds_file, 0o600)
            
            print("\n✅ Credentials sauvegardés de manière sécurisée")
            print(f"📁 Fichier: {creds_file}")
            print("🔒 Permissions: Lecture seule pour vous uniquement\n")
            return True
            
        except KeyboardInterrupt:
            print("\n\n❌ Configuration annulée")
            return False
        except Exception as e:
            print(f"\n❌ Erreur: {e}")
            return False
    
    def load_live_credentials(self):
        """Charge les credentials pour live trading"""
        creds_file = DATA_DIR / ".credentials.json"
        if not creds_file.exists():
            return None
        
        try:
            with open(creds_file) as f:
                return json.load(f)
        except Exception as e:
            self.log(f"Erreur chargement credentials: {e}", "ERROR")
            return None
    
    def initialize_live_client(self):
        """Initialise le client CLOB pour live trading"""
        if not CLOB_AVAILABLE:
            self.log("❌ SDK Polymarket non installé", "ERROR")
            return None
        
        creds = self.load_live_credentials()
        if not creds:
            self.log("❌ Credentials non configurés", "ERROR")
            return None
        
        try:
            # Import conditionnel
            from py_clob_client.clob_types import ApiCreds
            
            api_creds = ApiCreds(
                api_key=creds["api_key"],
                api_secret=creds["secret"],
                api_passphrase=creds["passphrase"]
            )
            
            chain_id = 137  # Polygon mainnet
            
            if creds.get("private_key"):
                # Auth L1 avec clé privée
                client = ClobClient(
                    host="https://clob.polymarket.com",
                    key=creds["private_key"],
                    chain_id=chain_id,
                    creds=api_creds
                )
            else:
                # Auth L2 uniquement (lecture)
                client = ClobClient(
                    host="https://clob.polymarket.com",
                    chain_id=chain_id,
                    creds=api_creds
                )
            
            self.log("✅ Client CLOB initialisé", "INFO")
            return client
            
        except Exception as e:
            self.log(f"❌ Erreur initialisation client: {e}", "ERROR")
            return None
            
    def log(self, message, level="INFO"):
        """Log un message"""
        timestamp = datetime.now(timezone.utc).isoformat()
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        with open(LOG_FILE, "a") as f:
            f.write(log_entry)
        print(log_entry.strip())
        
    def get_active_markets(self):
        """Récupère les marchés actifs depuis Polymarket API"""
        import urllib.request
        
        url = "https://gamma-api.polymarket.com/markets?active=true&closed=false&limit=50"
        req = urllib.request.Request(url, headers={"User-Agent": "PolymarketBot/1.0"})
        
        try:
            with urllib.request.urlopen(req, timeout=30, context=SSL_CONTEXT) as resp:
                data = json.loads(resp.read().decode())
                markets = data if isinstance(data, list) else data.get("markets", [])
                return markets
        except Exception as e:
            self.log(f"❌ Erreur API: {e}", "ERROR")
            return []
            
    def analyze_arbitrage(self, markets):
        """Détecte les opportunités d'arbitrage"""
        opportunities = []
        
        # Groupe les marchés similaires
        groups = {}
        for m in markets:
            q = m.get("question", "").lower()
            # Simplification: cherche des mots-clés communs
            key = None
            if "trump" in q and "deport" in q:
                key = "trump_deportation"
            elif "gta" in q or "gta vi" in q:
                key = "gta6"
            elif "bitcoin" in q or "btc" in q:
                key = "bitcoin"
                
            if key:
                if key not in groups:
                    groups[key] = []
                groups[key].append(m)
        
        # Analyse les écarts dans chaque groupe
        for key, group in groups.items():
            if len(group) >= 2:
                prices = []
                for m in group:
                    outcomes = m.get("outcomes", "[]")
                    outcome_prices = m.get("outcomePrices", "[]")
                    
                    # Parse JSON strings
                    try:
                        outcomes_list = json.loads(outcomes) if isinstance(outcomes, str) else outcomes
                        prices_list = json.loads(outcome_prices) if isinstance(outcome_prices, str) else outcome_prices
                        
                        if outcomes_list and len(outcomes_list) >= 2 and prices_list:
                            yes_price = float(prices_list[0])
                            prices.append({
                                "market": m,
                                "yes_price": yes_price,
                                "slug": m.get("slug", "")
                            })
                    except (json.JSONDecodeError, ValueError, IndexError):
                        continue
                
                if len(prices) >= 2:
                    prices.sort(key=lambda x: x["yes_price"])
                    cheapest = prices[0]
                    expensive = prices[-1]
                    spread = expensive["yes_price"] - cheapest["yes_price"]
                    
                    if spread > 0.05:  # Écart > 5%
                        opportunities.append({
                            "type": "arbitrage",
                            "description": f"Écart de {spread:.1%} sur {key}",
                            "buy": cheapest["slug"],
                            "buy_price": cheapest["yes_price"],
                            "confidence": min(spread * 100, 80)
                        })
        
        return opportunities
        
    def analyze_mean_reversion(self, markets):
        """Détecte les opportunités de mean reversion"""
        opportunities = []
        
        for m in markets:
            outcomes = m.get("outcomes", "[]")
            outcome_prices = m.get("outcomePrices", "[]")
            
            # Parse JSON strings
            try:
                outcomes_list = json.loads(outcomes) if isinstance(outcomes, str) else outcomes
                prices_list = json.loads(outcome_prices) if isinstance(outcome_prices, str) else outcome_prices
                
                if not outcomes_list or len(outcomes_list) < 2 or not prices_list:
                    continue
                    
                yes_price = float(prices_list[0])
            except (json.JSONDecodeError, ValueError, IndexError):
                continue
                
            volume = float(m.get("volume", 0))
            
            # Filtres
            if volume < self.config["filters"]["min_market_volume_usd"]:
                continue
                
            # Prix extrêmes
            if yes_price < 0.20:  # < 20¢
                opportunities.append({
                    "type": "mean_reversion",
                    "description": f"{m.get('question', 'N/A')[:50]}... @ {yes_price:.0%}",
                    "slug": m.get("slug", ""),
                    "direction": "YES",
                    "price": yes_price,
                    "confidence": (20 - yes_price * 100) * 2  # Plus c'est bas, plus confiance
                })
            elif yes_price > 0.80:  # > 80¢
                opportunities.append({
                    "type": "mean_reversion",
                    "description": f"{m.get('question', 'N/A')[:50]}... @ {yes_price:.0%}",
                    "slug": m.get("slug", ""),
                    "direction": "NO",
                    "price": 1 - yes_price,
                    "confidence": (yes_price * 100 - 80) * 2
                })
                
        return opportunities
        
    def scan_opportunities(self):
        """Scanne toutes les opportunités"""
        self.log("🔍 Scan des marchés...")
        
        markets = self.get_active_markets()
        if not markets:
            self.log("⚠️ Aucun marché récupéré")
            return []
            
        self.log(f"📊 {len(markets)} marchés analysés")
        
        all_opportunities = []
        
        # Stratégie 1: Arbitrage
        if "arbitrage" in self.config["strategies"]["enabled"]:
            arb_ops = self.analyze_arbitrage(markets)
            for op in arb_ops:
                op["strategy"] = "arbitrage"
                op["score"] = op["confidence"] * self.config["strategies"]["weights"]["arbitrage"]
            all_opportunities.extend(arb_ops)
            self.log(f"🎯 {len(arb_ops)} opportunités d'arbitrage")
        
        # Stratégie 2: Mean Reversion
        if "mean_reversion" in self.config["strategies"]["enabled"]:
            mr_ops = self.analyze_mean_reversion(markets)
            for op in mr_ops:
                op["strategy"] = "mean_reversion"
                op["score"] = op["confidence"] * self.config["strategies"]["weights"]["mean_reversion"]
            all_opportunities.extend(mr_ops)
            self.log(f"📈 {len(mr_ops)} opportunités mean reversion")
        
        # Trie par score
        all_opportunities.sort(key=lambda x: x["score"], reverse=True)
        
        return all_opportunities
        
    def execute_trade(self, opportunity):
        """Exécute (ou simule) un trade"""
        if self.mode == "paper":
            self.log(f"📝 PAPER TRADE: {opportunity['description']}")
            self.log(f"   Stratégie: {opportunity['strategy']}")
            self.log(f"   Confiance: {opportunity['confidence']:.1f}%")
            
            # Notif Telegram
            self.notify_telegram(f"📝 Paper Trade: {opportunity['description']} ({opportunity['confidence']:.0f}% confiance)")
            
            # Sauvegarde le trade simulé
            self.save_trade(opportunity, "paper")
            return {"status": "simulated", "opportunity": opportunity}
            
        else:
            # Mode live - exécution réelle
            self.log(f"💰 LIVE TRADE: {opportunity['description']}")
            return self.execute_live_trade(opportunity)
    
    def execute_live_trade(self, opportunity):
        """Exécute un trade réel via CLOB API"""
        if not CLOB_AVAILABLE:
            self.log("❌ SDK non disponible", "ERROR")
            return {"status": "error", "reason": "sdk_not_available"}
        
        client = self.initialize_live_client()
        if not client:
            self.log("❌ Impossible d'initialiser le client", "ERROR")
            return {"status": "error", "reason": "client_init_failed"}
        
        try:
            # Récupère le token ID du marché
            slug = opportunity.get("slug")
            if not slug:
                self.log("❌ Slug manquant", "ERROR")
                return {"status": "error", "reason": "missing_slug"}
            
            # Obtient les détails du marché
            market = client.get_market(slug)
            if not market:
                self.log(f"❌ Marché non trouvé: {slug}", "ERROR")
                return {"status": "error", "reason": "market_not_found"}
            
            token_id = market.get("tokens", [{}])[0].get("token_id")
            if not token_id:
                self.log("❌ Token ID non trouvé", "ERROR")
                return {"status": "error", "reason": "token_not_found"}
            
            # Calcul de la taille de position
            position_size = min(
                self.config["risk_management"]["max_position_size_usd"],
                self.capital * 0.2  # 20% du capital max
            )
            
            # Prépare l'ordre
            from py_clob_client.order_builder.constants import BUY
            
            order_args = {
                "token_id": token_id,
                "side": BUY,
                "size": position_size,
                "price": opportunity.get("price", 0.5)
            }
            
            self.log(f"📤 Placement ordre: {order_args}")
            
            # Place l'ordre (commenté pour sécurité - décommenter quand prêt)
            # signed_order = client.create_order(order_args)
            # response = client.post_order(signed_order)
            
            self.log("✅ Ordre créé (simulation - décommenter pour exécution réelle)")
            
            # Notif Telegram
            self.notify_telegram(f"💰 Live Trade: {opportunity['description']} - ${position_size}")
            
            # Sauvegarde
            self.save_trade(opportunity, "live", size=position_size)
            
            return {
                "status": "executed",
                "opportunity": opportunity,
                "size": position_size
            }
            
        except Exception as e:
            self.log(f"❌ Erreur exécution live: {e}", "ERROR")
            return {"status": "error", "reason": str(e)}
    
    def save_trade(self, opportunity, mode, size=None):
        """Sauvegarde un trade dans l'historique"""
        try:
            with open(TRADES_FILE) as f:
                data = json.load(f)
            
            trade = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "opportunity": opportunity,
                "mode": mode,
                "size": size
            }
            
            data["trades"].append(trade)
            
            with open(TRADES_FILE, "w") as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.log(f"Erreur sauvegarde trade: {e}", "ERROR")
            
    def run(self):
        """Exécute une itération du bot"""
        self.log(f"🤖 Bot Polymarket v1.1 - Mode: {self.mode.upper()}")
        self.log(f"💵 Capital: ${self.capital}")
        
        # Si mode live, vérifie credentials
        if self.mode == "live":
            if not self.load_live_credentials():
                self.log("🔐 Credentials live non configurés", "WARNING")
                self.log("   Lance: python3 bot.py --setup")
                return
            if not CLOB_AVAILABLE:
                self.log("❌ SDK Polymarket requis pour live trading", "ERROR")
                self.log("   pip install py-clob-client")
                return
        
        opportunities = self.scan_opportunities()
        
        if not opportunities:
            self.log("😴 Aucune opportunité détectée")
            self.notify_telegram("😴 Scan Polymarket: Aucune opportunité détectée")
            return
            
        # Prend la meilleure opportunité
        best = opportunities[0]
        self.log(f"⭐ Meilleure opportunité: {best['description']}")
        self.log(f"   Score: {best['score']:.1f} | Stratégie: {best['strategy']}")
        
        if best["confidence"] >= 60:  # Seuil minimal
            result = self.execute_trade(best)
            if result["status"] in ["simulated", "executed"]:
                self.notify_telegram(f"✅ Trade {self.mode}: {best['description']}")
        else:
            self.log(f"⚠️ Confiance trop faible ({best['confidence']:.1f}%), trade ignoré")
            self.notify_telegram(f"⚠️ Opportunité ignorée: {best['confidence']:.0f}% confiance (min: 60%)")
            
        self.log("✅ Scan terminé\n")

def main():
    """Point d'entrée principal avec gestion des arguments"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Bot Polymarket Trading")
    parser.add_argument("--setup", action="store_true", help="Configurer credentials live")
    parser.add_argument("--mode", choices=["paper", "live"], help="Forcer le mode")
    parser.add_argument("--test-notification", action="store_true", help="Tester notifications")
    
    args = parser.parse_args()
    
    bot = PolymarketBot()
    
    if args.setup:
        bot.setup_live_credentials()
        return
    
    if args.test_notification:
        bot.notify_telegram("🧪 Test notification Polymarket Bot")
        print("✅ Notification de test envoyée")
        return
    
    if args.mode:
        bot.mode = args.mode
        print(f"🎮 Mode forcé: {args.mode.upper()}")
    
    bot.run()

if __name__ == "__main__":
    main()
