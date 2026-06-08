from typing import Dict, Any, List
from src.state import DigestState
from src.tools.history_search import search_historical_football_facts 

class HistoireAgentNode:
    def __init__(self):
        pass

    def __call__(self, state: DigestState) -> Dict[str, Any]:
        print("[HistoireAgent] Récupération de l'anecdote historique basée sur le contexte global...")

        # 1. PEAUFINAGE : Extraction des faits réels de la semaine (Contexte Global)
        # Plutôt que de se baser sur de vagues instructions, on donne de la vraie matière à l'historien
        contexte_global = state.get("contexte_global", {})
        faits_semaine = ", ".join(contexte_global.get("faits_majeurs", []))
        tendances = contexte_global.get("tendance_du_moment", "")
        
        # On fusionne les consignes du planner et la réalité factuelle de la semaine
        recent_context = f"Faits marquants : {faits_semaine}. Tendance : {tendances}"
        
        if not faits_semaine:
            # Fallback si le contexte global est vide
            planned_sections = state.get("planned_sections", [])
            for section in planned_sections:
                if section.get("agent_type") == "historical_agent":
                    recent_context = section.get("instructions", "Actualité récente et grands matchs du moment")
                    break

        info_histoire_liste = []
        
        # 2. Appel de l'outil de minage historique
        try:
            print(f"[HistoireAgent] Envoi du contexte à la recherche d'archives : '{recent_context}'")
            resultats_historiques = search_historical_football_facts(recent_context=recent_context)
            
            if resultats_historiques:
                for res in resultats_historiques:
                    # STRUCTURE ADAPTÉE : On prépare le terrain pour le WriterAgent
                    # On crée la clé 'texte_redige' demandée pour l'assemblage final du journal
                    article_formate = {
                        "metadata": {
                            "source": "Wikipedia",
                            "annee": res.get("annee", "Histoire")
                        },
                        "data_brute": {
                            "titre_anecdote": res.get("titre_anecdote", ""),
                            "parallele_actuel": res.get("parallele_actuel", "")
                        },
                        # Le récit captivant devient l'article rédigé prêt pour le Markdown
                        "texte_redige": f"### LA MACHINE À REMONTER LE TEMPS : {res.get('titre_anecdote', 'Écho du Passé')}\n\n"
                                        f"*{res.get('parallele_actuel', '')}*\n\n"
                                        f"{res.get('recit', '')}\n\n"
                                        f"![Archive]({res.get('image_archive_url', 'https://images.unsplash.com/photo-1508098682722-e99c43a406b2')})"
                    }
                    info_histoire_liste.append(article_formate)
                
        except Exception as e:
            print(f"[HistoireAgent Error] Échec critique lors du traitement : {e}")
            # Fallback de secours respectant scrupuleusement la structure attendue
            info_histoire_liste.append({
                "metadata": {"source": "Fallback", "annee": "Histoire"},
                "data_brute": {"titre_anecdote": "Les échos du passé", "parallele_actuel": "La boucle du football se répète."},
                "texte_redige": "### LA MACHINE À REMONTER LE TEMPS : Les échos du passé\n\nL'histoire du football regorge d'anecdotes épiques et de scénarios légendaires qui font écho aux événements récents."
            })

        # 3. Envoi de la donnée collectée et rédigée dans le State (Clé synchronisée dans state.py)
        return {
            "info_histoire": info_histoire_liste
        }