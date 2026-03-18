"""
Nœud d'exécution d'outils sécurisé.

Responsabilité unique: exécuter les outils demandés par le LLM
en capturant les erreurs pour éviter de crasher l'agent.

Contrairement au ToolNode standard de LangGraph qui arrête tout
si un outil lève une exception, ce module:
  1. Attrape les exceptions
  2. Retourne un message d'erreur au LLM (au lieu de crasher)
  3. Log l'erreur pour le debugging
  4. Permet à l'agent de continuer avec les outils restants
"""

import time
from langchain_core.messages import ToolMessage
from config import logger


def create_safe_tool_node(tools: list):
    """
    Crée un nœud d'exécution d'outils avec gestion d'erreurs.
    
    Args:
        tools: Liste des outils LangChain disponibles
        
    Returns:
        Fonction compatible avec LangGraph qui exécute les outils
        de manière sécurisée
    """
    # Dictionnaire nom → outil pour retrouver l'outil rapidement
    tool_map = {tool.name: tool for tool in tools}
    
    def safe_tool_node(state: dict) -> dict:
        """
        Exécute les outils demandés par le LLM, avec gestion d'erreurs.
        
        Pour chaque tool_call dans le dernier message du LLM:
          - Trouve l'outil correspondant
          - L'exécute dans un try/except
          - Si succès → retourne le résultat comme ToolMessage
          - Si erreur → retourne un message d'erreur comme ToolMessage
        """
        last_message = state["messages"][-1]
        results = []
        new_errors = list(state.get("tool_errors", []))
        
        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_call_id = tool_call["id"]
            
            # Mesurer le temps d'exécution
            start = time.time()
            
            try:
                # Vérifier que l'outil existe
                if tool_name not in tool_map:
                    raise ValueError(f"Outil inconnu: '{tool_name}'")
                
                # Exécuter l'outil
                tool = tool_map[tool_name]
                result = tool.invoke(tool_args)
                elapsed = time.time() - start
                
                logger.info(f"✅ {tool_name}({tool_args}) → OK ({elapsed:.2f}s)")
                
                results.append(ToolMessage(
                    content=result,
                    tool_call_id=tool_call_id,
                    name=tool_name,
                ))
            
            except Exception as e:
                # L'outil a planté → on ne crashe PAS l'agent
                elapsed = time.time() - start
                error_msg = f"Erreur lors de l'exécution de {tool_name}: {str(e)}"
                
                logger.warning(f"❌ {tool_name}({tool_args}) → ERREUR ({elapsed:.2f}s): {e}")
                
                new_errors.append(error_msg)
                
                # Retourner l'erreur au LLM pour qu'il décide comment continuer
                results.append(ToolMessage(
                    content=f"ERREUR: {error_msg}. Continue avec les autres outils disponibles.",
                    tool_call_id=tool_call_id,
                    name=tool_name,
                ))
        
        return {
            "messages": results,
            "tool_errors": new_errors,
        }
    
    return safe_tool_node
