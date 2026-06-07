# src/graph.py

from langgraph.graph import StateGraph, END, START

# Synchronisation des imports avec ton arborescence réelle
from src.nodes.planner import PlannerNode
from src.nodes.historical_agent import HistoireAgentNode  
from src.nodes.validator import ValidatorAgentNode   # Corrigé (nom de fichier exact)
from src.nodes.general_agent import GeneralAgentNode
from src.nodes.stats_agent import StatsAgentNode
from src.nodes.mercato_agent import MercatoAgentNode
from src.nodes.scoop_team_agent import ScoopTeamAgentNode
from src.nodes.scoop_player_agent import ScoopPlayerAgentNode
from src.nodes.funny_agent import FunnyAgentNode
from src.nodes.writer import WriterAgentNode        # Corrigé (nom de fichier exact)
from src.state import DigestState

# src/graph.py

# src/graph.py

# 🆕 On crée une sécurité absolue au niveau du module au cas où le State LangGraph purge les clés à chaque loop de parallélisme
_GLOBAL_RETRY_COUNTER = 0

def route_after_validation(state: DigestState):
    """
    Routeur conditionnel après le Validator.
    Bloque définitivement la boucle infinie après 2 essais.
    """
    global _GLOBAL_RETRY_COUNTER
    
    status = state.get("validation_status")
    retry_agents = state.get("retry_agents", [])
    
    # Si le validator demande un RETRY
    if status == "RETRY" or len(retry_agents) > 0:
        _GLOBAL_RETRY_COUNTER += 1
        
        # 🚨 BARRIÈRE ABSOLUE : Si on a déjà tenté 2 fois, on FORCE le passage au Writer
        if _GLOBAL_RETRY_COUNTER > 2:
            print(f"\n🛑 [Router] Sécurité Anti-Boucle activée ! (Tentatives réelles : {_GLOBAL_RETRY_COUNTER}).")
            print("➡️ Forçage du passage au WriterAgent avec les données actuelles.\n")
            # Optionnel : réinitialiser pour la prochaine exécution globale du script
            _GLOBAL_RETRY_COUNTER = 0 
            return "writer"
            
        print(f"\n[Router] 🔄 Tentative de correction n°{_GLOBAL_RETRY_COUNTER} pour : {retry_agents}")
        return retry_agents

    # Si validé du premier coup
    print("\n[Router] 🎉 Validation réussie ! Envoi au Writer.")
    _GLOBAL_RETRY_COUNTER = 0
    return "writer"
def create_digest_graph():
    workflow = StateGraph(DigestState)
    
    # Définition du point d'entrée officiel
    workflow.add_edge(START, "planner")
    
    # 1. Ajout de tous les nœuds de l'équipe du Tableau Noir
    workflow.add_node("planner", PlannerNode())
    workflow.add_node("general_agent", GeneralAgentNode())
    workflow.add_node("histoire_agent", HistoireAgentNode())
    workflow.add_node("stats_agent", StatsAgentNode())
    workflow.add_node("mercato_agent", MercatoAgentNode())
    workflow.add_node("scoop_team_agent", ScoopTeamAgentNode())
    workflow.add_node("scoop_player_agent", ScoopPlayerAgentNode())
    workflow.add_node("funny_agent", FunnyAgentNode())
    workflow.add_node("validator", ValidatorAgentNode())
    workflow.add_node("writer", WriterAgentNode())
    
    # 2. FAN-OUT (Parallélisation corrigée)
    # Déclarer chaque edge individuellement résout le TypeError tout en forçant l'exécution parallèle
    workflow.add_edge("planner", "general_agent")
    workflow.add_edge("planner", "stats_agent")
    workflow.add_edge("planner", "mercato_agent")
    workflow.add_edge("planner", "scoop_team_agent")
    workflow.add_edge("planner", "scoop_player_agent")
    workflow.add_edge("planner", "histoire_agent")
    workflow.add_edge("planner", "funny_agent")
    
    # 3. FAN-IN (Barrière de synchronisation)
    # Le validator attend sagement que les 7 agents aient fini d'écrire dans le State
    workflow.add_edge("general_agent", "validator")
    workflow.add_edge("stats_agent", "validator")
    workflow.add_edge("mercato_agent", "validator")
    workflow.add_edge("scoop_team_agent", "validator")
    workflow.add_edge("scoop_player_agent", "validator")
    workflow.add_edge("histoire_agent", "validator")
    workflow.add_edge("funny_agent", "validator")
    
    # 4. ARBITRAGE DU WORKFLOW : Évaluation des structures JSON
    workflow.add_conditional_edges(
        "validator",
        route_after_validation,
        {
            "general_agent": "general_agent",
            "stats_agent": "stats_agent",
            "mercato_agent": "mercato_agent",
            "scoop_team_agent": "scoop_team_agent",
            "scoop_player_agent": "scoop_player_agent",
            "histoire_agent": "histoire_agent",
            "funny_agent": "funny_agent",
            "writer": "writer"
        }
    )
    
    # 5. Finalisation du document et fermeture du graphe
    workflow.add_edge("writer", END)
    
    return workflow.compile()

# Instanciation de l'application utilisable dans ton main.py
app = create_digest_graph()