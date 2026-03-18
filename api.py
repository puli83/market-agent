"""
Application FastAPI — Interface REST de l'agent d'analyse de marché.

Responsabilité unique: définir les endpoints HTTP et faire le pont
entre les requêtes API et l'orchestrateur (agent/graph.py).

Endpoints:
  - GET  /health     → Vérifier que le service est en ligne
  - POST /analyze    → Lancer une analyse de marché
  - GET  /docs       → Documentation Swagger interactive (auto-générée)

Après le lancement, ouvrir: http://localhost:8000/docs
"""

import time
from fastapi import FastAPI, HTTPException
from langchain_core.messages import HumanMessage

from config import settings, logger
from agent.graph import build_graph
from models.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    AnalysisStatus,
    HealthResponse,
)


# =============================================================================
# APPLICATION FASTAPI
# =============================================================================

app = FastAPI(
    title="Market Analysis Agent API",
    description=(
        "API d'analyse de marché e-commerce propulsée par un agent IA.\n\n"
        "L'agent orchestre 3 outils spécialisés:\n"
        "- **Web Scraper**: collecte les prix sur différentes plateformes\n"
        "- **Sentiment Analyzer**: analyse les avis clients bruts\n"
        "- **Trend Analyzer**: étudie les tendances de prix et de popularité\n\n"
        "Il produit ensuite un rapport stratégique complet avec des recommandations.\n\n"
        "**Produits disponibles (données mockées):** AirPods Pro 2, Nike Air Max 90, Nespresso Vertuo"
        "<u>Le rapport stratégique contient les sections suivantes</u>: \n\n"
        "**1.** *Résumé exécutif*. Cette section synthétise en quelques phrases les conclusions majeures et les points saillants de l'analyse pour offrir une vision d'ensemble immédiate.\n\n"
        "**2.** *Analyse des prix*. Ce volet détaille la structure tarifaire du marché, incluant les prix extrêmes et moyens, tout en identifiant les plateformes les plus compétitives et les écarts constatés.\n\n"
        "**3.** *Analyse du sentiment client*. Cette partie expose l'interprétation des avis bruts à travers un score global, l'identification des thématiques récurrentes et l'évaluation du taux de satisfaction.\n\n"
        "**4.** *Tendances et dynamique du marché*. Cette section analyse l'évolution des données chiffrées, la direction de la demande, la saisonnalité et le positionnement relatif face à la concurrence.\n\n"
        "**5.** *Recommandations stratégiques*. Le rapport se conclut par une série d'actions concrètes et priorisées, chacune étant directement justifiée par les données et les analyses présentées précédemment.\n\n"
    ),
    version="1.0.8",
)

# Construire le graphe une seule fois au démarrage.
# Le graphe est thread-safe et réutilisable pour chaque requête.
agent_graph = build_graph()
logger.info("🚀 Graphe LangGraph construit — API prête")


# =============================================================================
# ENDPOINT: Health Check
# =============================================================================

@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Vérifier la santé du service",
    tags=["Monitoring"],
)
async def health_check():
    """
    Retourne le statut du service.
    
    Utile pour Docker HEALTHCHECK, load balancers, et monitoring.
    """
    return HealthResponse(
        status="healthy",
        version="1.0.8",
        model=settings.model_name,
    )


# =============================================================================
# ENDPOINT: Analyse de marché
# =============================================================================

@app.post(
    "/analyze",
    response_model=AnalysisResponse,
    summary="Lancer une analyse de marché complète",
    tags=["Analyse"],
    responses={
        200: {
            "description": "Analyse complétée avec succès",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "product": "AirPods Pro 2",
                        "market": "france",
                        "report": "### 📊 RAPPORT D'ANALYSE DE MARCHÉ\n**Produit:** Apple AirPods Pro 2...",
                        "execution_time_seconds": 15.42,
                        "error": None,
                    }
                }
            },
        },
        500: {"description": "Erreur interne lors de l'analyse"},
    },
)
async def analyze_market(request: AnalysisRequest):
    """
    Lance une analyse de marché complète pour un produit donné.
    
    L'agent IA va automatiquement:
    1. Collecter les données de prix sur différentes plateformes
    2. Analyser le sentiment des avis clients (données brutes)
    3. Étudier les tendances du marché et la concurrence
    4. Compiler un rapport stratégique avec des recommandations
    
    **Exemples de requêtes:**
    
    Analyse simple:
    ```json
    {"product": "AirPods Pro 2"}
    ```
    
    Analyse avec marché et contexte:
    ```json
    {
        "product": "Nike Air Max 90",
        "market": "france",
        "context": "Je veux ouvrir une boutique de sneakers en ligne"
    }
    ```
    
    Autre produit:
    ```json
    {
        "product": "Nespresso Vertuo",
        "market": "canada",
        "context": "Évaluer le potentiel de revente sur marketplace"
    }
    ```
    """
    
    logger.info(f"📨 Requête reçue: {request.product} (marché: {request.market.value})")
    
    global_start = time.time()
    
    try:
        # --- Préparer l'état initial du graphe ---
        initial_state = {
            "messages": [
                HumanMessage(content=(
                    f"Analyse le marché pour: {request.product}. "
                    f"Marché cible: {request.market.value}. "
                    f"Contexte: {request.context or 'Aucun contexte spécifique'}. "
                    f"Utilise les 3 outils pour produire un rapport complet."
                ))
            ],
            "product": request.product,
            "market": request.market.value,
            "context": request.context,
            "iteration_count": 0,
            "start_time": global_start,
            "tool_errors": [],
        }
        
        # --- Exécuter le graphe ---
        report_content = None
        status = AnalysisStatus.SUCCESS
        
        for step in agent_graph.stream(initial_state):
            node_name = list(step.keys())[0]
            
            if node_name == "agent":
                agent_message = step["agent"]["messages"][-1]
                if not (hasattr(agent_message, "tool_calls") and agent_message.tool_calls):
                    report_content = agent_message.content
            
            elif node_name == "force_end":
                force_message = step["force_end"]["messages"][-1]
                report_content = force_message.content
                status = AnalysisStatus.PARTIAL
        
        elapsed = time.time() - global_start
        logger.info(f"✅ Analyse terminée en {elapsed:.2f}s — statut: {status.value}")
        
        return AnalysisResponse(
            status=status,
            product=request.product,
            market=request.market.value,
            report=report_content or "Aucun rapport généré.",
            execution_time_seconds=round(elapsed, 2),
        )
    
    except Exception as e:
        elapsed = time.time() - global_start
        logger.error(f"💥 Erreur: {e}")
        
        return AnalysisResponse(
            status=AnalysisStatus.ERROR,
            product=request.product,
            market=request.market.value,
            report="",
            execution_time_seconds=round(elapsed, 2),
            error=str(e),
        )
