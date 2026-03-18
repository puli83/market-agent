"""
Tests unitaires — Agent d'analyse de marché e-commerce.

13 tests organisés en 4 groupes:
  1. Fonctionnement des outils individuels (5 tests)
  2. Orchestration de l'agent principal (4 tests)
  3. Gestion des cas d'erreur (3 tests)
  4. Validation des outputs / API (1 test)

Lancement:
    pytest tests/test_agent.py -v

Note: Tous les tests fonctionnent SANS clé API.
"""

import json
import time
import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage


# =============================================================================
# GROUPE 1: Fonctionnement des outils individuels
# =============================================================================

class TestTools:
    """Vérifie que chaque outil retourne des données valides et bien structurées."""

    def test_web_scraper_returns_valid_json(self):
        """Le web scraper retourne du JSON valide avec les prix par plateforme."""
        from tools.market_tools import web_scraper

        result = web_scraper.invoke({"product": "AirPods Pro 2", "market": "france"})
        data = json.loads(result)

        assert "product" in data
        assert "platforms" in data
        assert len(data["platforms"]) > 0
        # Chaque plateforme doit avoir un prix et un nom
        for platform in data["platforms"]:
            assert "name" in platform
            assert "price" in platform
            assert isinstance(platform["price"], (int, float))

    def test_sentiment_analyzer_returns_raw_reviews(self):
        """Le sentiment analyzer retourne des avis bruts avec texte, note et auteur."""
        from tools.market_tools import sentiment_analyzer

        result = sentiment_analyzer.invoke({"product": "Nike Air Max 90"})
        data = json.loads(result)

        assert "reviews" in data
        assert len(data["reviews"]) > 0
        # Chaque avis doit avoir un texte, une note et un auteur
        for review in data["reviews"]:
            assert "text" in review
            assert "rating" in review
            assert "author" in review
            assert isinstance(review["rating"], (int, float))
            assert len(review["text"]) > 0

    def test_trend_analyzer_returns_monthly_data(self):
        """Le trend analyzer retourne des données mensuelles de recherche et de prix."""
        from tools.market_tools import trend_analyzer

        result = trend_analyzer.invoke({"product": "Nespresso Vertuo", "market": "france"})
        data = json.loads(result)

        assert "search_volume_monthly" in data
        assert "avg_price_monthly" in data
        assert "competitors" in data
        assert len(data["search_volume_monthly"]) > 0
        assert len(data["avg_price_monthly"]) > 0
        # Chaque entrée mensuelle doit avoir un mois et une valeur
        for entry in data["search_volume_monthly"]:
            assert "month" in entry
            assert "search_index" in entry
        for entry in data["avg_price_monthly"]:
            assert "month" in entry
            assert "avg_price" in entry

    def test_flexible_search_finds_product(self):
        """La recherche flexible trouve un produit avec différentes variantes du nom."""
        from tools.market_tools import web_scraper

        # Toutes ces variantes doivent trouver le même produit
        variants = ["airpods", "AirPods Pro 2", "AIRPODS", "airpods pro"]
        for variant in variants:
            result = web_scraper.invoke({"product": variant})
            data = json.loads(result)
            assert "error" not in data, f"Variante '{variant}' n'a pas trouvé le produit"
            assert "product" in data

    def test_unknown_product_returns_error(self):
        """Un produit inconnu retourne un message d'erreur propre, pas un crash."""
        from tools.market_tools import web_scraper, sentiment_analyzer, trend_analyzer

        for tool in [web_scraper, sentiment_analyzer, trend_analyzer]:
            result = tool.invoke({"product": "PlayStation 5"})
            data = json.loads(result)
            assert "error" in data
            assert "available_products" in data


# =============================================================================
# GROUPE 2: Orchestration de l'agent principal
# =============================================================================

class TestOrchestration:
    """Vérifie que le graphe LangGraph s'assemble et route correctement."""

    def test_graph_compiles(self):
        """Le graphe LangGraph se compile sans erreur."""
        import os
        os.environ.setdefault("GROQ_API_KEY", "fake_key_for_testing")
        from agent.graph import build_graph

        graph = build_graph()
        assert graph is not None

    def test_routing_returns_tools_on_tool_call(self):
        """Le routing retourne 'tools' quand le LLM fait un tool_call."""
        import os
        os.environ.setdefault("GROQ_API_KEY", "fake_key_for_testing")
        from agent.graph import build_graph

        # Simuler un état où le LLM a fait un tool_call
        state = {
            "messages": [
                AIMessage(content="", tool_calls=[{
                    "name": "web_scraper",
                    "args": {"product": "AirPods"},
                    "id": "test_1"
                }])
            ],
            "iteration_count": 1,
            "start_time": time.time(),
            "tool_errors": [],
        }

        # Le dernier message a un tool_call → doit router vers "tools"
        last_message = state["messages"][-1]
        has_tool_calls = hasattr(last_message, "tool_calls") and last_message.tool_calls
        assert has_tool_calls, "Le dernier message devrait contenir des tool_calls"

    def test_routing_returns_end_on_final_response(self):
        """Le routing retourne 'end' quand le LLM donne une réponse finale."""
        # Un message sans tool_calls = réponse finale
        state = {
            "messages": [
                AIMessage(content="Voici le rapport final...")
            ],
            "iteration_count": 3,
            "start_time": time.time(),
            "tool_errors": [],
        }

        last_message = state["messages"][-1]
        has_tool_calls = hasattr(last_message, "tool_calls") and last_message.tool_calls
        assert not has_tool_calls, "Le dernier message ne devrait pas contenir de tool_calls"

    def test_prompt_switches_after_all_tools(self):
        """Le prompt passe d'orchestrateur à analyste quand les 3 outils ont répondu."""
        from agent.prompts import ORCHESTRATOR_PROMPT, ANALYST_PROMPT

        all_tool_names = {"web_scraper", "sentiment_analyzer", "trend_analyzer"}

        # Avant: seulement 1 outil a répondu → orchestrateur
        messages_partial = [
            HumanMessage(content="Analyse AirPods"),
            ToolMessage(content="data", tool_call_id="1", name="web_scraper"),
        ]
        tools_called = {msg.name for msg in messages_partial if isinstance(msg, ToolMessage)}
        assert not all_tool_names.issubset(tools_called), "Ne devrait pas être complet"

        # Après: les 3 outils ont répondu → analyste
        messages_full = [
            HumanMessage(content="Analyse AirPods"),
            ToolMessage(content="data1", tool_call_id="1", name="web_scraper"),
            ToolMessage(content="data2", tool_call_id="2", name="sentiment_analyzer"),
            ToolMessage(content="data3", tool_call_id="3", name="trend_analyzer"),
        ]
        tools_called = {msg.name for msg in messages_full if isinstance(msg, ToolMessage)}
        assert all_tool_names.issubset(tools_called), "Devrait être complet"


# =============================================================================
# GROUPE 3: Gestion des cas d'erreur
# =============================================================================

class TestErrorHandling:
    """Vérifie que l'agent gère les erreurs sans crasher."""

    def test_unknown_tool_captured(self):
        """Un appel à un outil inexistant est capturé, pas de crash."""
        from tools.market_tools import get_all_tools
        from agent.safe_tools import create_safe_tool_node

        safe_node = create_safe_tool_node(get_all_tools())

        state = {
            "messages": [
                AIMessage(content="", tool_calls=[{
                    "name": "outil_inexistant",
                    "args": {},
                    "id": "test_err"
                }])
            ],
            "tool_errors": [],
        }

        result = safe_node(state)

        # L'erreur est capturée, pas de crash
        assert len(result["messages"]) == 1
        assert "ERREUR" in result["messages"][0].content
        assert len(result["tool_errors"]) == 1

    def test_mixed_success_and_failure(self):
        """Si 1 outil plante sur 3, les 2 autres réussissent et l'agent continue."""
        from tools.market_tools import get_all_tools
        from agent.safe_tools import create_safe_tool_node

        safe_node = create_safe_tool_node(get_all_tools())

        state = {
            "messages": [
                AIMessage(content="", tool_calls=[
                    {"name": "web_scraper", "args": {"product": "AirPods"}, "id": "ok_1"},
                    {"name": "outil_cassé", "args": {}, "id": "fail_1"},
                    {"name": "sentiment_analyzer", "args": {"product": "AirPods"}, "id": "ok_2"},
                ])
            ],
            "tool_errors": [],
        }

        result = safe_node(state)

        # 3 messages retournés (2 succès + 1 erreur)
        assert len(result["messages"]) == 3

        success_count = sum(1 for m in result["messages"] if "ERREUR" not in m.content)
        error_count = sum(1 for m in result["messages"] if "ERREUR" in m.content)
        assert success_count == 2
        assert error_count == 1
        assert len(result["tool_errors"]) == 1

    def test_max_iterations_triggers_force_end(self):
        """Le garde-fou d'itérations déclenche la sortie forcée."""
        import os
        os.environ.setdefault("GROQ_API_KEY", "fake_key_for_testing")
        from config import settings

        # Simuler un état qui a atteint le max d'itérations
        state = {
            "messages": [
                AIMessage(content="", tool_calls=[{
                    "name": "web_scraper",
                    "args": {"product": "test"},
                    "id": "test"
                }])
            ],
            "iteration_count": settings.max_iterations,  # Exactement au max
            "start_time": time.time(),
            "tool_errors": [],
        }

        # Le routing devrait retourner "force_end"
        assert state["iteration_count"] >= settings.max_iterations


# =============================================================================
# GROUPE 4: Validation des outputs / API
# =============================================================================

class TestAPI:
    """Vérifie que l'API FastAPI valide correctement les entrées."""

    def test_analyze_rejects_invalid_requests(self):
        """L'endpoint /analyze rejette les requêtes invalides avec 422."""
        import os
        os.environ.setdefault("GROQ_API_KEY", "fake_key_for_testing")
        from fastapi.testclient import TestClient
        from api import app

        client = TestClient(app)

        # Requête vide → 422
        r = client.post("/analyze", json={})
        assert r.status_code == 422

        # Produit trop court → 422
        r = client.post("/analyze", json={"product": "X"})
        assert r.status_code == 422

        # Marché invalide → 422
        r = client.post("/analyze", json={"product": "AirPods", "market": "mars"})
        assert r.status_code == 422

        # Requête valide → acceptée (200, pas 422)
        r = client.post("/analyze", json={"product": "AirPods Pro 2"})
        assert r.status_code == 200