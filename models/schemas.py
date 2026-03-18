"""
Schémas Pydantic pour la validation des données API.

Responsabilité unique: définir la structure exacte des requêtes et réponses.

FastAPI utilise ces modèles pour:
  - Valider automatiquement les données entrantes
  - Générer la documentation Swagger (les champs, types, exemples)
  - Sérialiser les réponses en JSON
"""

from pydantic import BaseModel, Field
from enum import Enum


# =============================================================================
# Requête d'analyse
# =============================================================================

class MarketRegion(str, Enum):
    """
    Régions de marché supportées.
    
    Un Enum garantit que l'utilisateur ne peut envoyer que des valeurs
    valides. FastAPI affichera ces options dans le dropdown Swagger.
    """
    FRANCE = "france"
    USA = "usa"
    CANADA = "canada"
    UK = "uk"
    GLOBAL = "global"


class AnalysisRequest(BaseModel):
    """
    Requête d'analyse de marché envoyée par l'utilisateur.
    
    Exemple de requête JSON:
        {
            "product": "AirPods Pro 2",
            "market": "france",
            "context": "Je veux vendre ce produit sur ma boutique en ligne"
        }
    """
    product: str = Field(
        ...,
        description="Nom du produit ou catégorie à analyser",
        examples=["AirPods Pro 2", "Nike Air Max 90", "Nespresso Vertuo"],
        min_length=2,
        max_length=200
    )
    market: MarketRegion = Field(
        default=MarketRegion.FRANCE,
        description="Région du marché à analyser"
    )
    context: str = Field(
        default="",
        description="Contexte additionnel pour personnaliser l'analyse",
        examples=["Je veux lancer ce produit sur ma boutique Shopify"],
        max_length=1000
    )


# =============================================================================
# Réponse d'analyse
# =============================================================================

class AnalysisStatus(str, Enum):
    """Statuts possibles d'une analyse."""
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"


class AnalysisResponse(BaseModel):
    """
    Réponse retournée après une analyse de marché.
    
    Exemple de réponse JSON:
        {
            "status": "success",
            "product": "AirPods Pro 2",
            "market": "france",
            "report": "## Analyse de marché - AirPods Pro 2 ...",
            "execution_time_seconds": 12.34,
            "error": null
        }
    """
    status: AnalysisStatus = Field(
        description="Statut de l'analyse (success, error, partial)"
    )
    product: str = Field(
        description="Produit analysé (repris de la requête)"
    )
    market: str = Field(
        description="Marché analysé"
    )
    report: str = Field(
        description="Rapport d'analyse complet généré par l'agent"
    )
    execution_time_seconds: float = Field(
        description="Durée de l'analyse en secondes"
    )
    error: str | None = Field(
        default=None,
        description="Message d'erreur si le statut n'est pas 'success'"
    )


# =============================================================================
# Réponse de santé (health check)
# =============================================================================

class HealthResponse(BaseModel):
    """
    Réponse du endpoint de santé.
    
    Utile pour Docker HEALTHCHECK, load balancers, et monitoring.
    """
    status: str = Field(description="État du service")
    version: str = Field(description="Version de l'API")
    model: str = Field(description="Modèle LLM utilisé")
