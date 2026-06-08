import json 
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage
from src.state import DigestState
from src.tools.agent_context_shared import resolve_primary_team, create_groq_llm

class GeneralAgentNode:
    def __init__(self):
        # Température basse pour une synthèse factuelle et structurée des résultats
        self.llm = create_groq_llm(temperature=0.2)
        
    def __call__(self, state: DigestState) -> Dict[str, Any]:
        print("[GeneralAgent] Synthèse des résultats majeurs et de l'actualité globale...")
        
        club_phare = resolve_primary_team(state)
        
        # 1. Récupération directe de la matière collectée par le GlobalContextAgent
        contexte_global = state.get("contexte_global", {})
        faits_semaine = ", ".join(contexte_global.get("faits_majeurs", []))
        scores_semaine = ", ".join(contexte_global.get("scores_marquants", []))
        tendance = contexte_global.get("tendance_du_moment", "")
        
        system_prompt = (
            "Tu es le Rédacteur en Chef Adjoint du magazine 'Le Tableau Noir'.\n"
            "Ton rôle est de prendre les fils d'actualité bruts de la semaine pour en faire la grande synthèse de "
            "couverture du journal (la revue de presse des faits marquants et des chocs mondiaux).\n\n"
            "Consignes impératives :\n"
            "1. Ne fais pas de listes d'objets JSON complexes inutilisables.\n"
            "2. Rédige un article journalistique complet, fluide, captivant et structuré au format Markdown dans la clé 'texte_redige'.\n"
            "3. L'article doit mettre en avant les dossiers chauds de la semaine et mentionner l'impact sur le paysage footballistique actuel.\n\n"
            "Tu dois obligatoirement répondre sous ce format JSON strict :\n"
            "{\n"
            "  \"data_brute\": {\n"
            "     \"competition_principale\": \"Le nom du tournoi ou focus majeur de la semaine\",\n"
            "     \"nombre_faits_analyses\": 3\n"
            "  },\n"
            "  \"texte_redige\": \"Ton grand article de synthèse complet en Markdown (avec titres, sous-titres, et paragraphes rédigés)...\"\n"
            "}"
        )
        
        user_content = f"""
        Club de référence de l'utilisateur : {club_phare}
        
        [FIL D'ACTUALITÉ BRUT DE LA SEMAINE] :
        - Faits saillants repérés : {faits_semaine or "Aucun fait majeur à signaler."}
        - L'ambiance / Tendance : {tendance or "Calme plat."}
        - Les scores notables : {scores_semaine or "Pas de choc enregistré."}
        """

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_content)
        ]
        
        info_general_liste = []
        try:
            # Invocation en mode JSON Object strict via Groq
            response = self.llm.invoke(messages, response_format={"type": "json_object"})
            parsed_general = json.loads(response.content)
            
            # Structuration finale avec encapsulation de la rubrique
            article_formate = {
                "metadata": {
                    "source": "Revue de Presse Globale"
                },
                "data_brute": parsed_general.get("data_brute", {}),
                # On applique directement le titre de section
                "texte_redige": f"## TOUR D'HORIZON : L'actualité de la semaine\n\n{parsed_general.get('texte_redige', '')}"
            }
            info_general_liste.append(article_formate)
            
        except Exception as e:
            print(f"[GeneralAgent Error] Échec critique du parsing de l'actualité générale : {e}")
            info_general_liste.append({
                "metadata": {"source": "Fallback"},
                "data_brute": {"competition_principale": "Général", "nombre_faits_analyses": 0},
                "texte_redige": "## TOUR D'HORIZON : Les affaires courantes\n\nL'actualité mondiale s'est concentrée sur les dossiers de fond et la logistique interne des fédérations cette semaine. Pas de séisme majeur sur la planète football."
            })

        # Renvoi de la clé exacte configurée dans state.py
        return {
            "info_general": info_general_liste
        }