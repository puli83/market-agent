"""
Outils spécialisés de l'agent d'analyse de marché.

Responsabilité unique: définir les outils appelables par le LLM
via le mécanisme de function calling.

3 outils disponibles:
  1. web_scraper        → Prix et infos produit par plateforme
  2. sentiment_analyzer → Avis clients bruts
  3. trend_analyzer     → Tendances de recherche, prix, concurrence

Chaque outil:
  - Est décoré avec @tool (LangChain) → devient appelable par le LLM
  - Reçoit un nom de produit en entrée
  - Cherche les données dans data/mock_data.py
  - Retourne un JSON structuré
"""

import json
from langchain_core.tools import tool
from data.mock_data import SCRAPER_DATA, SENTIMENT_DATA, TRENDS_DATA


# =============================================================================
# Fonction utilitaire: recherche flexible dans les données mockées
# =============================================================================

def find_product(product_query: str, data_dict: dict) -> dict | None:
    """
    Cherche un produit dans un dictionnaire de données mockées.
    
    La recherche est flexible: "AirPods Pro 2", "airpods", ou "airpods pro"
    trouveront tous le même produit.
    
    Args:
        product_query: Ce que l'utilisateur a tapé (ex: "AirPods Pro")
        data_dict:     Dictionnaire de données à fouiller
    
    Returns:
        Les données du produit trouvé, ou None si aucun match
    """
    query = product_query.lower().strip()
    
    for key, value in data_dict.items():
        if query in key or key in query:
            return value
    
    return None


# =============================================================================
# Outil 1: Web Scraper
# =============================================================================

@tool
def web_scraper(product: str, market: str = "france") -> str:
    """Collecte les prix et informations d'un produit sur différentes plateformes e-commerce.

    Retourne les prix, notes, nombre d'avis et disponibilité sur 
    Amazon, Fnac, Cdiscount, et d'autres plateformes selon le produit.

    Args:
        product: Nom du produit à rechercher (ex: "AirPods Pro 2")
        market: Marché cible (ex: "france")

    Returns:
        JSON avec les données produit par plateforme
    """
    data = find_product(product, SCRAPER_DATA)
    
    if data is None:
        return json.dumps({
            "error": f"Produit '{product}' non trouvé dans la base de données.",
            "available_products": list(SCRAPER_DATA.keys()),
            "suggestion": "Essayez avec un des produits disponibles."
        }, ensure_ascii=False)
    
    return json.dumps(data, ensure_ascii=False, indent=2)


# =============================================================================
# Outil 2: Sentiment Analyzer
# =============================================================================

@tool
def sentiment_analyzer(product: str) -> str:
    """Analyse les avis clients d'un produit et extrait les insights clés.

    Retourne les avis clients bruts collectés sur différentes plateformes.
    Le LLM doit analyser ces avis pour en tirer le sentiment global,
    les thèmes récurrents et les signaux d'alerte.

    Args:
        product: Nom du produit à analyser (ex: "Nike Air Max 90")

    Returns:
        JSON avec les avis clients bruts à analyser
    """
    data = find_product(product, SENTIMENT_DATA)
    
    if data is None:
        return json.dumps({
            "error": f"Aucun avis trouvé pour '{product}'.",
            "available_products": list(SENTIMENT_DATA.keys()),
            "suggestion": "Essayez avec un des produits disponibles."
        }, ensure_ascii=False)
    
    return json.dumps(data, ensure_ascii=False, indent=2)


# =============================================================================
# Outil 3: Trend Analyzer
# =============================================================================

@tool
def trend_analyzer(product: str, market: str = "france") -> str:
    """Analyse les tendances de prix, de popularité et la position concurrentielle d'un produit.

    Retourne les données brutes mensuelles: indices de recherche,
    prix moyens, et concurrents. Le LLM doit interpréter ces chiffres
    pour identifier les tendances.

    Args:
        product: Nom du produit à analyser (ex: "Nespresso Vertuo")
        market: Marché cible (ex: "france")

    Returns:
        JSON avec données brutes de tendances à interpréter
    """
    data = find_product(product, TRENDS_DATA)
    
    if data is None:
        return json.dumps({
            "error": f"Aucune donnée de tendance pour '{product}'.",
            "available_products": list(TRENDS_DATA.keys()),
            "suggestion": "Essayez avec un des produits disponibles."
        }, ensure_ascii=False)
    
    return json.dumps(data, ensure_ascii=False, indent=2)


# =============================================================================
# Registre: liste tous les outils disponibles
# =============================================================================

def get_all_tools() -> list:
    """
    Retourne la liste de tous les outils pour l'agent.
    
    Pour ajouter un nouvel outil:
      1. Créer la fonction avec @tool
      2. L'ajouter à cette liste
    """
    return [web_scraper, sentiment_analyzer, trend_analyzer]
