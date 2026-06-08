# src/nodes/general_agent.py

from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from src.state import DigestState
from src.tools.agent_context_shared import create_groq_llm
from src.tools.web_search import web_search  # Ou le nom exact de ton outil de recherche
import json

class GeneralAgentNode:
    def __init__(self):
        # Température équilibrée pour une belle plume journalistique
        self.model = create_groq_llm(temperature=0.5)

    def __call__(self, state: DigestState) -> Dict[str, Any]:
        print("[GeneralAgent] Synthèse des résultats majeurs et de l'actualité globale mondiale...")

        # 1. Force la recherche sur l'actualité internationale globale (exit le Real Madrid)
        query_recherche = "football actualité chaude infos majeures"
        
        try:
            # Appel à ton outil de recherche DDG existant
            search_results = web_search(query_recherche, max_results=5)
        except Exception as e:
            print(f"[GeneralAgent] Erreur recherche web: {e}")
            search_results = "Aucun résultat internet récent."

        # 2. Prompt 100% axé sur le Football Mondial
        system_prompt = (
            "Tu es le Grand Reporter de 'Le Tableau Noir'. Ton rôle est de rédiger un tour d'horizon de l'actualité marquante du football international à partir des données fournies."

            "Ne présuppose jamais de la période de l'année. S'il s'agit de compétitions internationales, analyse les sélections. S'il s'agit de championnats de clubs, analyse les clubs. Si les données internet sont vides (période creuse), transforme ta chronique en un éditorial de fond sur un grand fait marquant du football moderne."

            "⚠️ DIRECTIVE DE SÉCURITÉ FORMAT JSON :\n"
            "Tu dois impérativement répondre sous la forme d'un objet JSON strict contenant exactement ces deux clés :\n"
            "1. 'data_brute': Un dictionnaire des faits marquants récupérés.\n"
            "2. 'texte_redige': Ta chronique complète rédigée en Markdown (sans afficher le titre global de la rubrique H1).\n"
            "ATTENTION : Échappe obligatoirement chaque saut de ligne avec '\\n' pour que le JSON reste parfaitement valide.\n\n"
            
            "⚠️ GESTION DE LA TRÊVE (FALLBACK) :\n"
            "Si les données de recherche sont pauvres ou vides, ne te plains pas. Rédige un tour d'horizon analytique "
            "sur les forces en présence pour les matchs internationaux de l'été 2026 ou le bilan global de la saison européenne qui vient de s'achever."
        )

        user_content = f"""
        Données fraîches du web concernant le football mondial :
        {search_results}
        
        Période : {state.get('time_window', 'cette semaine')} (Juin 2026)
        """

        try:
            response = self.model.invoke(
                [SystemMessage(content=system_prompt), HumanMessage(content=user_content)],
                response_format={"type": "json_object"}
            )
            
            # Parsing sécurisé du JSON de l'agent
            result_json = json.loads(response.content)
            
        except Exception as e:
            print(f"[GeneralAgent Error] Échec de la génération ou du parsing JSON : {e}")
            # Fallback de secours élégant pour le validateur
            result_json = {
                "data_brute": {"status": "fallback_mondial"},
                "texte_redige": (
                    "## TOUR D'HORIZON : LE FOOTBALL MONDIAL EN TRANSITION\\n\\n"
                    "L'Europe du football retient son souffle en ce début de mois de juin 2026. "
                    "Alors que les championnats domestiques ont rendu leur verdict final, les regards se tournent désormais "
                    "vers les rassemblements des sélections nationales et les premières grandes manœuvres des fédérations internationales."
                )
            }

        # 3. Retour calé sur ton canal d'accumulation du State
        return {
            "info_general": [
                {
                    "metadata": {"source": "Cellule Presse Internationale", "date": "Juin 2026"},
                    "data_brute": result_json.get("data_brute", {}),
                    "texte_redige": result_json.get("texte_redige", "")
                }
            ]
        }
    

    
