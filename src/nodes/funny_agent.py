import json 
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage
from src.state import DigestState
from src.tools.web_search import web_search
from src.tools.agent_context_shared import resolve_primary_team, build_football_query, create_groq_llm

class FunnyAgentNode:
    def __init__(self):
        # Température un peu plus haute pour laisser de la liberté et de l'humour au LLM
        self.llm = create_groq_llm(temperature=0.6)
        
    def __call__(self, state: DigestState) -> Dict[str, Any]:
        print("[FunnyAgent] Recherche de la dose d'insolence et de dérision...")
        
        club_phare = resolve_primary_team(state)
        
        # 📋 LES SPÉCIALISTES DU SOURIRE ET DU TROLL FOOTBALLISTIQUE
        sites_humour = [
            "sofoot.com",               # Le ton décalé par excellence
            "cahiersdufootball.net",    # L'ironie fine et la critique des dérives
            "winamax.fr/sport",         # L'humour incisif, vannes sur les flops
            "legorafi.fr"               # Pour capter l'esprit parodique si sujet foot
        ]

        print("[FunnyAgent] Capture des mèmes et des moments insolites du football européen...")
        query_global = build_football_query("foot insolite", "humour declaration")
        raw_global_data = web_search.invoke({
            "query": query_global, 
            "target_sites": sites_humour, 
            "max_results": 5
        })
        
        print(f"[FunnyAgent] Recherche de vannes ou situations cocasses sur {club_phare}...")
        query_team = build_football_query("so foot", club_phare)
        raw_team_data = web_search.invoke({
            "query": query_team, 
            "target_sites": sites_humour, 
            "max_results": 4
        })
        
        system_prompt = (
            "Tu es le rédacteur satirique (l'esprit 'So Foot / Winamax Sport') du magazine 'Le Tableau Noir'.\n"
            "Ton rôle est d'apporter de l'ironie, du second degré, de pointer du doigt les déclarations absurdes, "
            "les simulations ridicules ou les actions insolites de la semaine.\n\n"
            "Analyse les données fournies et renvoie STRICTEMENT ce format JSON :\n"
            "{\n"
            "  \"les_perles_europe\": [\n"
            "     {\"cible\": \"Joueur/Club\", \"vanne_ou_fait\": \"La punchline ou la situation ridicule racontée de manière caustique\"}\n"
            "  ],\n"
            "  \"le_troll_du_club\": {\n"
            "     \"sujet\": \"Le point d'ancrage de la moquerie sur le club phare\",\n"
            "     \"blague\": \"Une remarque ironique bien sentie sur leur forme ou un fait de match récent.\"\n"
            "  }\n"
            "}"
        )
        
        user_content = f"""
        Club phare : {club_phare}
        
        [DONNÉES INSOLITES EUROPE] :
        {raw_global_data}
        
        [DONNÉES MOQUERIES/CONTEXTE {str(club_phare).upper()}] :
        {raw_team_data}
        """

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_content)
        ]
        
        info_funny = []
        try:
            response = self.llm.invoke(messages, response_format={"type": "json_object"})
            info_funny.append(json.loads(response.content))
        except Exception as e:
            print(f"[FunnyAgent Error] Échec du parsing : {e}")
            info_funny.append({
                "les_perles_europe": [],
                "le_troll_du_club": {"sujet": "Calme plat", "blague": "Pas de drama cette semaine, le service de sécurité a bien fermé les portes."}
            })

        return {"info_funny": info_funny}