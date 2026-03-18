"""
Construction du graphe LangGraph — cœur de l'orchestration.

Responsabilité unique: assembler les nœuds, les arêtes et la logique
de routing en un graphe exécutable.

Architecture du graphe:

                    ┌─────────────────────────────────────┐
                    │                                     │
                    ▼                                     │
    START ──→ agent_node ──→ should_continue()            │
              (LLM pense)       │                         │
                                │                         │
                    ┌───────────┼───────────┐             │
                    │           │           │             │
                    ▼           ▼           ▼             │
              LLM veut    LLM a fini   Garde-fou         │
              un outil    son rapport   déclenché         │
                    │           │           │             │
                    ▼           ▼           ▼             │
              safe_tool_node   END    force_end_node      │
              (exécute l'outil)       (rapport partiel)   │
                    │                       │             │
                    │                       ▼             │
                    │                      END            │
                    │                                     │
                    └─────────────────────────────────────┘
                        résultat retourné à l'agent

    Prompts utilisés:
      ● agent_node (0-2 outils collectés) → ORCHESTRATOR_PROMPT
      ● agent_node (3 outils collectés)   → ANALYST_PROMPT
      ● force_end_node                    → ANALYST_PROMPT + FORCE_END_PROMPT

L'agent suit le pattern ReAct (Reason + Act):
  1. agent_node: le LLM reçoit un prompt adapté à la phase (orchestration ou analyse)
  2. should_continue(): vérifie les garde-fous puis route selon la réponse du LLM
  3. safe_tool_node: exécute l'outil avec gestion d'erreurs, retourne à agent_node
  4. La boucle se répète jusqu'à ce que le LLM produise son rapport final

Utilisation:
    from agent.graph import build_graph
    graph = build_graph()
    result = graph.invoke(initial_state)
"""

import time
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

from config import settings, logger
from agent.state import AgentState
from agent.prompts import ORCHESTRATOR_PROMPT, ANALYST_PROMPT, FORCE_END_PROMPT
from langchain_core.messages import ToolMessage
from agent.safe_tools import create_safe_tool_node
from tools.market_tools import get_all_tools


def build_graph():
    """
    Construit et compile le graphe d'orchestration de l'agent.
    
    Le graphe a 3 nœuds:
      - "agent":     Le LLM réfléchit et décide (appeler un outil ou conclure)
      - "tools":     Exécute l'outil demandé de manière sécurisée
      - "force_end": Compile un rapport partiel quand un garde-fou se déclenche
    
    Returns:
        Graphe LangGraph compilé, prêt à être invoqué
    """
    
    # --- Préparer le LLM et les outils ---
    tools = get_all_tools()
    
    llm = ChatGroq(
        model=settings.model_name,
        temperature=settings.temperature,
    )
    
    # bind_tools() informe le LLM des outils disponibles via function calling
    llm_with_tools = llm.bind_tools(tools)
    
    # --- Nœud Agent: le LLM réfléchit ---
    # Noms des 3 outils pour détecter quand tous ont été appelés
    all_tool_names = {t.name for t in tools}
    
    def agent_node(state: AgentState) -> dict:
        """
        Le LLM analyse la situation et décide: appeler un outil ou conclure.
        
        Utilise DEUX PROMPTS selon la phase:
          - ORCHESTRATOR_PROMPT: tant que tous les outils n'ont pas été appelés
          - ANALYST_PROMPT: quand les 3 outils ont retourné leurs données
        """
        current_iteration = state.get("iteration_count", 0) + 1
        
        # Détecter quels outils ont déjà retourné des résultats
        tools_called = {
            msg.name for msg in state["messages"]
            if isinstance(msg, ToolMessage)
        }
        all_tools_done = all_tool_names.issubset(tools_called)
        
        # Choisir le prompt adapté à la phase
        if all_tools_done:
            prompt = ANALYST_PROMPT
            logger.info(f"📊 Analyste — itération {current_iteration}/{settings.max_iterations} (3/3 outils collectés)")
        else:
            prompt = ORCHESTRATOR_PROMPT
            logger.info(f"🤖 Orchestrateur — itération {current_iteration}/{settings.max_iterations} ({len(tools_called)}/3 outils collectés)")
        
        system = SystemMessage(content=prompt)
        messages = [system] + state["messages"]
        
        start = time.time()
        response = llm_with_tools.invoke(messages)
        elapsed = time.time() - start
        
        logger.info(f"   LLM répondu en {elapsed:.2f}s")
        
        return {
            "messages": [response],
            "iteration_count": current_iteration,
        }
    
    # --- Nœud Outils: exécution sécurisée ---
    safe_tool_node = create_safe_tool_node(tools)
    
    # --- Routing: continuer, terminer, ou forcer l'arrêt ---
    def should_continue(state: AgentState) -> str:
        """
        Détermine la prochaine étape avec les garde-fous.
        
        Ordre de vérification:
          1. Timeout global dépassé ?    → "force_end"
          2. Max itérations atteint ?    → "force_end"
          3. Le LLM veut un outil ?      → "tools"
          4. Sinon                       → "end"
        """
        # Garde-fou 1: Timeout
        elapsed = time.time() - state.get("start_time", time.time())
        if elapsed > settings.timeout_seconds:
            logger.warning(f"⏰ TIMEOUT: {elapsed:.0f}s (max: {settings.timeout_seconds}s)")
            return "force_end"
        
        # Garde-fou 2: Max itérations
        if state.get("iteration_count", 0) >= settings.max_iterations:
            logger.warning(f"🔄 MAX ITÉRATIONS: {settings.max_iterations} atteint")
            return "force_end"
        
        # Routing normal
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        
        return "end"
    
    # --- Nœud de sortie forcée ---
    def force_end_node(state: AgentState) -> dict:
        """
        Compile un rapport partiel quand un garde-fou se déclenche.
        
        Appelle le LLM SANS outils pour le forcer à conclure
        avec les données déjà collectées.
        """
        logger.info("⚠️ Sortie forcée — compilation du rapport partiel")
        
        force_message = HumanMessage(content=FORCE_END_PROMPT)
        system = SystemMessage(content=ANALYST_PROMPT)
        messages = [system] + state["messages"] + [force_message]
        
        # LLM sans outils → il ne peut que répondre
        llm_no_tools = ChatGroq(
            model=settings.model_name,
            temperature=settings.temperature,
        )
        response = llm_no_tools.invoke(messages)
        
        return {"messages": [response]}
    
    # --- Assembler le graphe ---
    graph = StateGraph(AgentState)
    
    graph.add_node("agent", agent_node)
    graph.add_node("tools", safe_tool_node)
    graph.add_node("force_end", force_end_node)
    
    graph.set_entry_point("agent")
    
    graph.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END,
            "force_end": "force_end",
        }
    )
    
    graph.add_edge("tools", "agent")
    graph.add_edge("force_end", END)
    
    return graph.compile()
