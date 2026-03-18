"""
Configuration centralisée de l'application.

Ce module est le SEUL endroit où on lit les variables d'environnement
et où on configure le logging. Tous les autres modules importent depuis ici.

Responsabilité unique: configuration et constantes.

Utilisation:
    from config import settings, logger
    logger.info(f"Modèle: {settings.model_name}")
"""

import os
import logging
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()


# =============================================================================
# LOGGING
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("market-agent")


# =============================================================================
# SETTINGS
# =============================================================================

class Settings:
    """
    Paramètres de l'application, lus depuis les variables d'environnement.
    
    Centraliser ici évite d'avoir des os.getenv() éparpillés dans le code.
    Si une valeur n'est pas définie dans .env, la valeur par défaut est utilisée.
    """
    
    # --- LLM ---
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    model_name: str = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")
    temperature: float = float(os.getenv("TEMPERATURE_MODEL", 0.3))
    
    # --- Garde-fous ---
    max_iterations: int = int(os.getenv("MAX_ITERATIONS", 10))
    timeout_seconds: int = int(os.getenv("TIMEOUT_SECONDS", 120))


# Instance unique, importable partout
settings = Settings()


# =============================================================================
# VÉRIFICATION DE LA CLÉ API
# =============================================================================

def check_api_key():
    """
    Vérifie que la clé API Groq est configurée.
    
    Appelée une seule fois au démarrage (dans main.py).
    Arrête le programme avec un message clair si la clé manque.
    """
    if not settings.groq_api_key:
        logger.error("=" * 60)
        logger.error("Clé API Groq manquante!")
        logger.error("")
        logger.error("1. Copie .env.example en .env:")
        logger.error("   cp .env.example .env")
        logger.error("")
        logger.error("2. Obtiens une clé gratuite sur:")
        logger.error("   https://console.groq.com/keys")
        logger.error("")
        logger.error("3. Colle-la dans le fichier .env")
        logger.error("=" * 60)
        exit(1)
