import json 
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage
from src.state import DigestState
from src.tools.web_search import web_search
from src.tools.agent_context_shared import resolve_primary_team, build_football_query, create_groq_llm

class ScoopPlayerAgentNode:
    def __init__(self):
        self.llm = create_groq_llm(temperature=0.2)
        
    def __call__(self, state: DigestState) -> Dict[str, Any]:
        print("[ScoopPlayerAgent] Analyse des performances et déclas des superstars...")
        
        club_phare = resolve_primary_team(state)
        
        # 📋 LISTE DES SITES IDÉAUX POUR LE SUIVI DES INDIVIDUALITÉS
        sites_stars = [
            "lequipe.fr",           # France (Notes des joueurs, interviews exclusives)
            "as.com",               # Espagne (Focus individualités / Real Madrid / Barça)
            "mundodeportivo.com",   # Espagne (Focus individualités Barça / Stars mondiales)
            "theathletic.com",      # Angleterre (Portraits profonds et interviews de joueurs)
            "kicker.de",            # Allemagne (Analyses de performances de la Bundesliga)
            "gazzetta.it",          # Italie (Les notes mythiques de la Gazzetta)
            "eurosport.fr"          # Actu générale des grands joueurs européens
        ]

        print("[ScoopPlayerAgent] Recherche des actus brûlantes sur les joueurs stars mondiaux...")
        query_global = build_football_query("declaration", "performance joueur star")
        raw_global_data = web_search.invoke({
            "query": query_global, 
            "target_sites": sites_stars, 
            "max_results": 5
        })
        
        print(f"[ScoopPlayerAgent] Recherche des dossiers chauds sur les joueurs de {club_phare}...")
        query_team = build_football_query("joueur declaration", club_phare)
        raw_team_data = web_search.invoke({
            "query": query_team, 
            "target_sites": sites_stars, 
            "max_results": 5
        })
        
        system_prompt = (
            "Tu es le paparazzi expert des superstars du football mondial pour 'Le Tableau Noir'.\n"
            "Tu traques les déclas chocs, les coups d'éclat, les polémiques ou les records brisés par les grands joueurs.\n\n"
            "Analyse les données fournies et renvoie STRICTEMENT ce format JSON :\n"
            "{\n"
            "  \"stars_globales\": [\n"
            "     {\"joueur\": \"Nom complet\", \"club\": \"Club actuel\", \"evenement\": \"Ce qui fait parler de lui (déclaration, record, clash...)\"}\n"
            "  ],\n"
            "  \"focus_joueur_equipe\": {\n"
            "     \"joueur_en_vue\": \"Nom du joueur le plus en vue au club phare\",\n"
            "     \"analyse_actu\": \"Pourquoi il fait l'actualité en ce moment (stat, décla, méforme...)\"\n"
            "  }\n"
            "}"
        )
        
        user_content = f"""
        Club phare : {club_phare}
        
        [DONNÉES STARS MONDIALES] :
        {raw_global_data}
        
        [DONNÉES JOUEURS DE {str(club_phare).upper()}] :
        {raw_team_data}
        """

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_content)
        ]
        
        info_scoop_player = []
        try:
            response = self.llm.invoke(messages, response_format={"type": "json_object"})
            info_scoop_player.append(json.loads(response.content))
        except Exception as e:
            print(f"[ScoopPlayerAgent Error] Échec du parsing : {e}")
            info_scoop_player.append({
                "stars_globales": [],
                "focus_joueur_equipe": {"joueur_en_vue": "Non déterminé", "analyse_actu": "Analyse en cours."}
            })

        return {"info_scoop_player": info_scoop_player}