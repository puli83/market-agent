"""
Point d'entrée de l'application.

Lance le serveur FastAPI qui expose l'agent d'analyse de marché
via une API REST.

Utilisation:
    python main.py

Puis ouvrir dans le navigateur:
    http://localhost:8000/docs    → Interface Swagger (tester l'API)
    http://localhost:8000/health  → Vérifier que le service est en ligne

Exemples de requêtes avec curl:

    # Analyse simple
    curl -X POST http://localhost:8000/analyze \\
      -H "Content-Type: application/json" \\
      -d '{"product": "AirPods Pro 2"}'

    # Analyse avec contexte
    curl -X POST http://localhost:8000/analyze \\
      -H "Content-Type: application/json" \\
      -d '{"product": "Nike Air Max 90", "market": "france", "context": "boutique Shopify"}'

    # Health check
    curl http://localhost:8000/health
"""

import uvicorn
from config import settings, logger, check_api_key


def main():
    """Lance le serveur FastAPI."""
    
    # Vérifier la clé API avant de démarrer
    check_api_key()
    
    logger.info("=" * 60)
    logger.info("🚀 Démarrage de l'API Market Analysis Agent")
    logger.info(f"   Modèle LLM:   {settings.model_name}")
    logger.info(f"   Température:   {settings.temperature}")
    logger.info(f"   Max itérations: {settings.max_iterations}")
    logger.info(f"   Timeout:       {settings.timeout_seconds}s")
    logger.info("")
    logger.info("   📖 Swagger UI: http://localhost:8000/docs")
    logger.info("   ❤️  Health:     http://localhost:8000/health")
    logger.info("=" * 60)
    
    # Lancer le serveur Uvicorn
    # - "api:app" : importe l'objet 'app' depuis le fichier 'api.py'
    # - host 0.0.0.0 : écoute sur toutes les interfaces (nécessaire pour Docker)
    # - reload : redémarre quand le code change (pratique en développement)
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8010,
        reload=True,
    )


if __name__ == "__main__":
    main()
