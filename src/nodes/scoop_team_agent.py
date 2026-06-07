import json 
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage
from src.state import DigestState
from src.tools.web_search import web_search
from src.tools.agent_context_shared import resolve_primary_team, build_football_query, create_groq_llm

class ScoopTeamAgentNode:
    def __init__(self):
        self.llm = create_groq_llm(temperature=0.3)
        
    def __call__(self, state: DigestState) -> Dict[str, Any]:
        print("[ScoopTeamAgent] Infiltration dans les vestiaires du Big Five...")
        
        club_phare = resolve_primary_team(state)
        
        # 📋 LISTE DES MEILLEURS INDISCRETS DU VESTIAIRE
        sites_coulisses = [
            "theathletic.com",       # Le patron mondial des coulisses et enquêtes de vestiaire
            "rmcsport.bfmtv.com",    # France (Exclusivités, vestiaire PSG/Liga/Premier League)
            "lequipe.fr",           # France (Enquêtes internes clubs)
            "marca.com",            # Espagne (Les secrets du Real Madrid)
            "sport.es",             # Espagne (Les secrets du FC Barcelone)
            "bild.de",              # Allemagne (Le service secret du Bayern Munich)
            "gazzetta.it",          # Italie (Les crises de club en Serie A)
            "corrieredellosport.it" # Italie (Coulisses chaudes de la Serie A)
        ]

        print("[ScoopTeamAgent] Recherche des grosses crises et secrets des clubs européens...")
        query_global = build_football_query("crise", "ambiance vestiaire")
        raw_global_data = web_search.invoke({
            "query": query_global, 
            "target_sites": sites_coulisses, 
            "max_results": 5
        })
        
        print(f"[ScoopTeamAgent] Recherche de révélations internes sur {club_phare}...")
        query_team = build_football_query("vestiaire", club_phare)
        raw_team_data = web_search.invoke({
            "query": query_team, 
            "target_sites": sites_coulisses, 
            "max_results": 5
        })
        
        system_prompt = (
            "Tu es l'agent infiltré (le 'James Bond' des vestiaires) du magazine 'Le Tableau Noir'.\n"
            "Ton but est de dénicher les secrets, tensions, changements de coachs ou choix tactiques forts.\n\n"
            "Analyse les données fournies et renvoie STRICTEMENT ce format JSON :\n"
            "{\n"
            "  \"scoops_europe\": [\n"
            "     {\"club\": \"Nom du Club\", \"titre\": \"Titre accrocheur\", \"revelation\": \"Résumé de la tension ou de l'info interne\"}\n"
            "  ],\n"
            "  \"focus_coulisses_equipe\": {\n"
            "     \"ambiance\": \"État du vestiaire du club phare (Tensions, unité, doutes...)\",\n"
            "     \"info_cle\": \"La révélation principale de la semaine sur ce club\"\n"
            "  }\n"
            "}"
        )
        
        user_content = f"""
        Club phare : {club_phare}
        
        [DONNÉES COULISSES EUROPE] :
        {raw_global_data}
        
        [DONNÉES REVELATIONS {str(club_phare).upper()}] :
        {raw_team_data}
        """

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_content)
        ]
        
        info_scoop_team = []
        try:
            response = self.llm.invoke(messages, response_format={"type": "json_object"})
            info_scoop_team.append(json.loads(response.content))
        except Exception as e:
            print(f"[ScoopTeamAgent Error] Échec du parsing : {e}")
            info_scoop_team.append({
                "scoops_europe": [],
                "focus_coulisses_equipe": {"ambiance": "Stable", "info_cle": "Rien à signaler dans le vestiaire."}
            })

        return {"info_scoop_team": info_scoop_team}