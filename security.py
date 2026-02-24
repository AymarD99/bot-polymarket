#!/usr/bin/env python3
"""
🔐 Sécurité - Chiffrement des credentials
Utilise Fernet (symétrique) pour protéger les clés API
"""

import os
import json
import base64
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

DATA_DIR = Path(__file__).parent.parent / "data"
CREDS_FILE = DATA_DIR / ".credentials.enc"
SALT_FILE = DATA_DIR / ".salt"

def get_or_create_salt():
    """Récupère ou crée un salt unique"""
    if SALT_FILE.exists():
        return SALT_FILE.read_bytes()
    else:
        salt = os.urandom(16)
        SALT_FILE.write_bytes(salt)
        os.chmod(SALT_FILE, 0o600)
        return salt

def derive_key(password: str, salt: bytes) -> bytes:
    """Dérive une clé de chiffrement depuis un mot de passe"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

def encrypt_credentials(credentials: dict, password: str):
    """Chiffre les credentials"""
    salt = get_or_create_salt()
    key = derive_key(password, salt)
    f = Fernet(key)
    
    data = json.dumps(credentials).encode()
    encrypted = f.encrypt(data)
    
    CREDS_FILE.write_bytes(encrypted)
    os.chmod(CREDS_FILE, 0o600)
    
def decrypt_credentials(password: str) -> dict:
    """Déchiffre les credentials"""
    if not CREDS_FILE.exists():
        return None
        
    salt = get_or_create_salt()
    key = derive_key(password, salt)
    f = Fernet(key)
    
    try:
        encrypted = CREDS_FILE.read_bytes()
        decrypted = f.decrypt(encrypted)
        return json.loads(decrypted)
    except Exception:
        return None  # Mauvais mot de passe
