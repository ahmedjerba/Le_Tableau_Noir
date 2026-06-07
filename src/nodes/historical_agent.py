from typing import Dict, Any, List
from src.state import DigestState
from src.tools.history_search import search_historical_football_facts 

class HistoireAgentNode:
    def __init__(self):
        pass

    def __call__(self, state: DigestState) -> Dict[str, Any]:
        print("[HistoireAgent] Récupération de l'anecdote historique basée sur le contexte global...")

        # 1. Extraction des consignes contextuelles du Planner
        planned_sections = state.get("planned_sections", [])
        focus_instructions = "Actualité récente et grands matchs du moment"
        
        for section in planned_sections:
            if section.get("agent_type") == "historical_agent":
                focus_instructions = section.get("instructions", focus_instructions)
                break

        recent_context = focus_instructions
        info_histoire_liste = []
        
        # 2. Appel de l'outil de minage historique (qui renvoie le format JSON encapsulé)
        try:
            print(f"[HistoireAgent] Envoi du contexte à la recherche d'archives : '{recent_context}'")
            resultats_historiques = search_historical_football_facts(recent_context=recent_context)
            
            if resultats_historiques:
                info_histoire_liste.extend(resultats_historiques)
                
        except Exception as e:
            print(f"[HistoireAgent Error] Échec critique lors du traitement : {e}")
            # Fallback de secours identique à la structure JSON attendue
            info_histoire_liste.append({
                "titre_anecdote": "Les échos du passé",
                "annee": "Histoire",
                "recit": "L'histoire du football regorge d'anecdotes épiques et de scénarios légendaires qui font écho aux événements récents.",
                "parallele_actuel": "La boucle du football se répète.",
                "image_archive_url": "https://images.unsplash.com/photo-1508098682722-e99c43a406b2"
            })

        # 3. Envoi de la donnée collectée structurée dans le State
        return {
            "info_histoire": info_histoire_liste
        }