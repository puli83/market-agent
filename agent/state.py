"""
État du graphe LangGraph.

Responsabilité unique: définir la structure de données qui circule
à travers le graphe d'exécution de l'agent.

Chaque nœud du graphe (agent, tools, force_end) peut lire et modifier
cet état. L'annotation 'add_messages' fait que les messages s'accumulent
au fil des appels (au lieu d'être écrasés).
"""

from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    Structure de données partagée entre tous les nœuds du graphe.
    
    Champs constants (ne changent pas pendant l'exécution):
        product:   Produit à analyser (ex: "AirPods Pro 2")
        market:    Marché cible (ex: "france")
        context:   Contexte additionnel de l'utilisateur
    
    Champs dynamiques (évoluent à chaque itération):
        messages:        Historique des échanges LLM ↔ outils
        iteration_count: Compteur de tours dans la boucle (garde-fou)
        start_time:      Timestamp de début d'analyse (pour le timeout)
        tool_errors:     Liste des erreurs d'outils rencontrées
    """
    
    # Historique de conversation — le reducer 'add_messages' ajoute
    # les nouveaux messages à la fin au lieu d'écraser la liste
    messages: Annotated[list[BaseMessage], add_messages]
    
    # Paramètres de la requête
    product: str
    market: str
    context: str
    
    # Garde-fous
    iteration_count: int
    start_time: float
    tool_errors: list[str]
