# src/graph.py

from langgraph.graph import StateGraph, END, START

# 1. Synchronisation rigoureuse des imports (6 agents experts restants)
from src.nodes.planner import PlannerNode
from src.nodes.general_agent import GeneralAgentNode
from src.nodes.stats_agent import StatsAgentNode
from src.nodes.mercato_agent import MercatoAgentNode
from src.nodes.club_specialist_agent import ScoopTeamAgentNode  # Ton agent infiltré unique
from src.nodes.historical_agent import HistoireAgentNode  
from src.nodes.funny_agent import FunnyAgentNode
from src.nodes.validator import ValidatorAgentNode  
from src.nodes.writer import WriterAgentNode        
from src.state import DigestState

# Sécurité anti-boucle infinie au niveau du module
_GLOBAL_RETRY_COUNTER = 0

def route_after_validation(state: DigestState):
    """
    Routeur conditionnel après le Validator.
    Permet de renvoyer uniquement les agents en échec ou de passer au Writer.
    """
    global _GLOBAL_RETRY_COUNTER
    
    status = state.get("validation_status")
    retry_agents = state.get("retry_agents", [])
    
    # Si le validator demande un RETRY
    if status == "RETRY" or len(retry_agents) > 0:
        _GLOBAL_RETRY_COUNTER += 1
        
        # 🚨 BARRIÈRE ABSOLUE : Après 2 tentatives infructueuses, on force le passage
        if _GLOBAL_RETRY_COUNTER > 2:
            print(f"\n🛑 [Router] Sécurité Anti-Boucle activée ! (Tentatives réelles : {_GLOBAL_RETRY_COUNTER}).")
            print("➡️ Forçage du passage au WriterAgent avec les données actuelles.\n")
            _GLOBAL_RETRY_COUNTER = 0 
            return "writer"
            
        print(f"\n[Router] 🔄 Tentative de correction n°{_GLOBAL_RETRY_COUNTER} pour : {retry_agents}")
        # LangGraph va activer en parallèle uniquement les nœuds dont les chaînes sont dans la liste
        return retry_agents

    # Si validé avec succès
    print("\n[Router] 🎉 Validation réussie ! Envoi au Rédacteur en Chef (Writer).")
    _GLOBAL_RETRY_COUNTER = 0
    return "writer"


def create_digest_graph():
    workflow = StateGraph(DigestState)
    
    # Définition du point d'entrée officiel
    workflow.add_edge(START, "planner")
    
    # 2. Ajout de tous les nœuds de la rédaction (L'équipe de 6 agents + Outils)
    workflow.add_node("planner", PlannerNode())
    workflow.add_node("general_agent", GeneralAgentNode())
    workflow.add_node("stats_agent", StatsAgentNode())
    workflow.add_node("mercato_agent", MercatoAgentNode())
    workflow.add_node("scoop_team_agent", ScoopTeamAgentNode())  # Alimente info_club_specialiste
    workflow.add_node("histoire_agent", HistoireAgentNode())
    workflow.add_node("funny_agent", FunnyAgentNode())
    workflow.add_node("validator", ValidatorAgentNode())
    workflow.add_node("writer", WriterAgentNode())
    
    # 3. FAN-OUT (Parallélisation propre vers nos 6 spécialistes)
    workflow.add_edge("planner", "general_agent")
    workflow.add_edge("planner", "stats_agent")
    workflow.add_edge("planner", "mercato_agent")
    workflow.add_edge("planner", "scoop_team_agent")
    workflow.add_edge("planner", "histoire_agent")
    workflow.add_edge("planner", "funny_agent")
    
    # 4. FAN-IN (Barrière de synchronisation : attend que les 6 aient fini)
    workflow.add_edge("general_agent", "validator")
    workflow.add_edge("stats_agent", "validator")
    workflow.add_edge("mercato_agent", "validator")
    workflow.add_edge("scoop_team_agent", "validator")
    workflow.add_edge("histoire_agent", "validator")
    workflow.add_edge("funny_agent", "validator")
    
    # 5. ARBITRAGE DU WORKFLOW : Redirection ciblée ou finale
    workflow.add_conditional_edges(
        "validator",
        route_after_validation,
        {
            "general_agent": "general_agent",
            "stats_agent": "stats_agent",
            "mercato_agent": "mercato_agent",
            "scoop_team_agent": "scoop_team_agent",
            "histoire_agent": "histoire_agent",
            "funny_agent": "funny_agent",
            "writer": "writer"
        }
    )
    
    # Finalisation du document et fermeture du graphe
    workflow.add_edge("writer", END)
    
    return workflow.compile()

# Instanciation de l'application prête à l'emploi
app = create_digest_graph()