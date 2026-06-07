# src/state.py

import operator
from typing import TypedDict, List, Dict, Any, Annotated

class DigestState(TypedDict):
    """État partagé entre les agents pour la construction du digest 'Le Tableau Noir'."""
    user_preferences: Dict[str, Any]
    time_window: str
    sections_to_write: List[str]
    
    # Données collectées par les agents (Clés synchronisées en JSON strict)
    info_general: Annotated[List[Dict[str, Any]], operator.add]           # Mis à jour
    info_stats: Annotated[List[Dict[str, Any]], operator.add]             # Mis à jour
    info_funny: Annotated[List[Dict[str, Any]], operator.add]             # Mis à jour
    info_mercato: Annotated[List[Dict[str, Any]], operator.add]
    info_scoop_sur_equipe: Annotated[List[Dict[str, Any]], operator.add]
    info_scoop_sur_joueur: Annotated[List[Dict[str, Any]], operator.add]
    info_histoire: Annotated[List[Dict[str, Any]], operator.add]
    
    # Planification & Routage
    planned_sections: List[Dict[str, Any]]
    validation_status: str
    retry_agents: List[str]
    
    # Rapport final
    final_markdown: str
    status: str