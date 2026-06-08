import operator
from typing import TypedDict, List, Dict, Any, Annotated

class DigestState(TypedDict):
    """État partagé entre les agents pour la construction du digest 'Le Tableau Noir'."""
    user_preferences: Dict[str, Any]
    time_window: str
    sections_to_write: List[str]
    
    # --- BRANCHE CONTEXTE GLOBAL ---
    # Contient les dates, compétitions majeures et scores généraux validés pour Juin 2026
    contexte_global: Dict[str, Any]
    
    # --- BRANCHE CONTEXTE ÉQUIPE ---
    # Contient les infos de dernière minute et l'état de l'équipe ciblée pour Juin 2026
    contexte_equipe: Dict[str, Any]
    
    # --- DONNÉES ET ARTICLES RÉDIGÉS ---
    # Chaque dictionnaire de la liste contiendra désormais :
    # {
    #    "metadata": {"source": "...", "date": "2026"}, 
    #    "data_brute": {...}, 
    #    "texte_redige": "Le paragraphe journalistique complet..."
    # }
    info_general: Annotated[List[Dict[str, Any]], operator.add]          
    info_stats: Annotated[List[Dict[str, Any]], operator.add]            
    info_funny: Annotated[List[Dict[str, Any]], operator.add]            
    info_mercato: Annotated[List[Dict[str, Any]], operator.add]
    info_histoire: Annotated[List[Dict[str, Any]], operator.add]
    
    # L'agent unique pour l'équipe concernée (Fusion de scoop joueur et équipe)
    info_club_specialiste: Annotated[List[Dict[str, Any]], operator.add]
    
    # Planification & Routage
    planned_sections: List[Dict[str, Any]]
    validation_status: str
    retry_agents: List[str]
    
    # Rapport final (L'assemblage de tous les "texte_redige" en Markdown)
    final_markdown: str
    status: str