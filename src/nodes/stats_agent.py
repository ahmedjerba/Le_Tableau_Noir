# src/nodes/stats_agent.py

import json 
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage
from src.state import DigestState
from src.tools.web_search import web_search
from src.tools.agent_context_shared import resolve_primary_team, build_football_query, create_groq_llm

class StatsAgentNode:
    def __init__(self):
        # On utilise une température très basse (0.1) pour forcer le LLM à être 
        # extrêmement rigoureux avec les chiffres et éviter toute hallucination de data.
        self.llm = create_groq_llm(temperature=0.1)
        
    def __call__(self, state: DigestState) -> Dict[str, Any]:
        print("[StatsAgent] Extraction des métriques avancées et structures de performance...")
        
        # Récupération dynamique de l'équipe ciblée par le rapport
        club_phare = resolve_primary_team(state)
        
        # 📋 SITES CIBLES : Les références mondiales absolues de la data football
        sites_stats = [
            "theanalyst.com",       # Opta Analyst (Modèles mathématiques, analyses tactiques profondes)
            "fbref.com",            # La mine d'or (Scouting, xG accumulés, pressings, tacles)
            "understat.com",        # Les pionniers des Expected Goals (xG) détaillés par match
            "sofascore.com",        # Notes algorithmiques basées sur les actions de jeu
            "whoscored.com"         # Caractéristiques d'équipes et forces/faiblesses chiffrées
        ]

        # 1. Recherche des grandes tendances statistiques en Europe
        print("[StatsAgent] Scan des grosses anomalies statistiques européennes...")
        query_global = build_football_query("stats advancement xg", "tactique performance")
        raw_global_data = web_search.invoke({
            "query": query_global, 
            "target_sites": sites_stats, 
            "max_results": 5
        })
        
        # 2. Recherche spécifique sur la data du club phare
        print(f"[StatsAgent] Analyse des rapports métriques pour l'équipe : {club_phare}...")
        query_team = build_football_query("metrics xG performance", club_phare)
        raw_team_data = web_search.invoke({
            "query": query_team, 
            "target_sites": sites_stats, 
            "max_results": 5
        })
        
        # 3. Prompt de structuration : On impose au LLM de n'extraire que de la vraie donnée chiffrée
        system_prompt = (
            "Tu es le 'Data Scientist' en chef du magazine 'Le Tableau Noir'.\n"
            "Tu as horreur des phrases vagues comme 'ils ont bien joué' ou 'l'attaque est efficace'.\n"
            "Tu ne jures que par les chiffres froids : Expected Goals (xG), passes progressives, "
            "pressings réussis dans le dernier tiers, intensité défensive (PPDA).\n\n"
            "Analyse le matériel de recherche fourni et extrait les faits chiffrés. "
            "Tu dois STRICTEMENT retourner ce format JSON :\n"
            "{\n"
            "  \"statistiques_europe\": [\n"
            "     {\n"
            "       \"sujet\": \"Nom du joueur ou de l'équipe engagée\",\n"
            "       \"metrique\": \"La statistique clé précise avec son unité (ex: 2.45 xG, 89% de passes progressives)\",\n"
            "       \"explication\": \"Ce que ce chiffre traduit concrètement sur la domination ou la faiblesse tactique.\"\n"
            "     }\n"
            "  ],\n"
            "  \"focus_data_equipe\": {\n"
            "     \"metrique_cle_club\": \"Le chiffre marquant ou l'anomalie statistique de la semaine pour le club phare\",\n"
            "     \"analyse_tactique\": \"Ton interprétation de cette statistique sur l'animation de jeu actuelle de l'équipe.\"\n"
            "  }\n"
            "}"
        )
        
        user_content = f"""
        Club cible prioritaire : {club_phare}
        
        [FLUX DE DONNÉES STATS EUROPE] :
        {raw_global_data}
        
        [FLUX DE DONNÉES SPÉCIFIQUES {str(club_phare).upper()}] :
        {raw_team_data}
        """

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_content)
        ]
        
        info_stats_liste = []
        try:
            # Forcer la réponse au format JSON strict via Groq
            response = self.llm.invoke(messages, response_format={"type": "json_object"})
            parsed_data = json.loads(response.content)
            info_stats_liste.append(parsed_data)
            
        except Exception as e:
            print(f"[StatsAgent Error] Échec de parsing ou de génération des statistiques : {e}")
            # Fallback structurellement valide pour ne pas casser la suite du graphe
            info_stats_liste.append({
                "statistiques_europe": [],
                "focus_data_equipe": {
                    "metrique_cle_club": "Data indisponible",
                    "analyse_tactique": "Les algorithmes de tracking n'ont pas pu remonter de métriques fiables pour cette session."
                }
            })

        # 4. On pousse la liste JSON dans la clé dédiée du State global
        return {
            "info_stats": info_stats_liste
        }