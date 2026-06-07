import json 
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage
from src.state import DigestState
from src.tools.web_search import web_search
from src.tools.agent_context_shared import resolve_primary_team, build_football_query, create_groq_llm

class GeneralAgentNode:
    def __init__(self):
        self.llm = create_groq_llm(temperature=0.2)
        
    def __call__(self, state: DigestState) -> Dict[str, Any]:
        print("[GeneralAgent] Collecte des résultats majeurs et faits marquants du football mondial...")
        
        club_phare = resolve_primary_team(state)
        
        # 📋 LES GRANDS GÉNÉRALISTES DE L'ACTU FOOTBALL
        sites_generaux = [
            "lequipe.fr",           # Référence France
            "eurosport.fr",         # Europe & Omnisport football
            "flashscore.fr",        # Résultats, classements et faits bruts
            "bbc.com/sport/football"# Référence internationale incontournable
        ]

        print("[GeneralAgent] Synthèse des résultats des grands championnats et coupes d'Europe...")
        query_global = build_football_query("football", "resultats classements actualite")
        raw_global_data = web_search.invoke({
            "query": query_global, 
            "target_sites": sites_generaux, 
            "max_results": 5
        })
        
        print(f"[GeneralAgent] Vérification des dernières dépêches pour {club_phare}...")
        query_team = build_football_query("football match resume", club_phare)
        raw_team_data = web_search.invoke({
            "query": query_team, 
            "target_sites": sites_generaux, 
            "max_results": 5
        })
        
        system_prompt = (
            "Tu est le Rédacteur en Chef Adjoint du magazine 'Le Tableau Noir'.\n"
            "Tu t'assures que les grands résultats, les classements mis à jour et les événements majeurs "
            "ne passent pas à la trappe.\n\n"
            "Analyse les données fournies et renvoie STRICTEMENT ce format JSON :\n"
            "{\n"
            "  \"actualites_majeures\": [\n"
            "     {\"competition\": \"Nom (ex: Ligue des Champions)\", \"evenement\": \"Le fait marquant (ex: Défaite surprise du Real)\", \"impact\": \"Impact au classement ou dynamique\"}\n"
            "  ],\n"
            "  \"synthese_equipe_phare\": {\n"
            "     \"dernier_resultat\": \"Score ou résumé très court du dernier match du club phare\",\n"
            "     \"situation_classement\": \"Où en est le club dans sa compétition principale\"\n"
            "  }\n"
            "}"
        )
        
        user_content = f"""
        Club phare : {club_phare}
        
        [DONNÉES INFOS GÉNÉRALES EUROPE] :
        {raw_global_data}
        
        [DONNÉES CLUBACTU {str(club_phare).upper()}] :
        {raw_team_data}
        """

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_content)
        ]
        
        info_general = []
        try:
            response = self.llm.invoke(messages, response_format={"type": "json_object"})
            info_general.append(json.loads(response.content))
        except Exception as e:
            print(f"[GeneralAgent Error] Échec du parsing : {e}")
            info_general.append({
                "actualites_majeures": [],
                "synthese_equipe_phare": {"dernier_resultat": "Non renseigné", "situation_classement": "En cours d'évaluation."}
            })

        return {"info_general": info_general}