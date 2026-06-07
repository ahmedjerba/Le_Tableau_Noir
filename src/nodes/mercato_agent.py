import json 
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage
from src.state import DigestState
from src.tools.web_search import web_search
from src.tools.agent_context_shared import resolve_primary_team, build_football_query, create_groq_llm

class MercatoAgentNode:
    def __init__(self):
        self.llm = create_groq_llm(temperature=0.2)
        
    def __call__(self, state: DigestState) -> Dict[str, Any]:
        print("[MercatoAgent] Analyse du marché des transferts en cours...")
        
        club_phare = resolve_primary_team(state)
        planned_sections = state.get("planned_sections", [])
        team_target = None
        for section in planned_sections:
            if section.get("agent_type") == "mercato_agent":
                team_target = section.get("target")
                break
        if not team_target:
            preferences = state.get("user_preferences", {})
            teams = preferences.get("teams", [])
            team_target = teams[0] if teams else club_phare
            time_window = state.get("time_window", "les derniers jours")
        
        # 📋 LISTE DES SITES EXPERTS DU BIG FIVE POUR LE MERCATO
        sites_mercato = [
            "footmercato.net",       # France (Réactivité)
            "maxifoot.fr",          # France (Revue de presse)
            "skysports.com",        # Angleterre (Breaking news)
            "theathletic.com",      # Angleterre / Monde (Fiabilité chirurgicale)
            "marca.com",            # Espagne (Proche Real Madrid)
            "as.com",               # Espagne (Actu Liga)
            "bild.de",              # Allemagne (Proche Bayern / Bundesliga)
            "gazzetta.it"           # Italie (Le boss de la Serie A)
        ]

        print("[MercatoAgent] Recherche des tendances et gros coups mondiaux sur les sites experts...")
        query_global = build_football_query("transferts", "officiels")
        # Injection de la liste de sites ici ⬇️
        raw_global_data = web_search.invoke({
            "query": query_global, 
            "target_sites": sites_mercato, 
            "max_results": 5
        })
        
        print(f"[MercatoAgent] Recherche de rumeurs spécifiques à {team_target} sur les sites experts...")
        query_team = build_football_query("mercato", team_target or club_phare)
        # Injection de la liste de sites ici ⬇️
        raw_team_data = web_search.invoke({
            "query": query_team, 
            "target_sites": sites_mercato, 
            "max_results": 5
        })
        
        system_prompt = (
            "Règle de recherche: génère STRICTEMENT des requêtes de 2 à 4 mots maximum, uniquement en FRANÇAIS."
            " Le premier mot doit être 'football' ou 'foot'. Interdis les guillemets imbriqués, les mots temporels inutiles"
            " comme 'cette semaine', 'actuel', 'récent', et tout mélange anglais/français.\n\n"
            "Tu es le spécialiste des transferts (le 'Fabrizio Romano') du magazine 'Le Tableau Noir'.\n"
            "Analyse les données du web fournies pour construire la rubrique mercato.\n\n"
            "Tu dois impérativement extraire :\n"
            "1. 4 informations générales majeures sur le mercato mondial.\n"
            "2. 2 informations spécifiques et rumeurs concernant le club phare si elles existent.\n\n"
            "Pour CHAQUE information ou rumeur, tu dois évaluer sa fiabilité et attribuer un pourcentage :\n"
            "- Si le transfert est officiel, signé ou annoncé par le club : mets STRICTEMENT 100%.\n"
            "- Si c'est une rumeur en cours de négociation : estime la probabilité entre 10% et 95% selon la solidité des sources.\n\n"
            "Tu dois obligatoirement répondre sous ce format JSON strict :\n"
            "{\n"
            "  \"mercato_global\": [\n"
            "     {\"joueur\": \"Nom\", \"details\": \"Résumé de l'info\", \"provenance_destination\": \"Club A -> Club B\", \"pourcentage_fiabilite\": \"100% (Officialisé)\"}\n"
            "  ],\n"
            "  \"mercato_equipe\": [\n"
            "     {\"joueur\": \"Nom\", \"details\": \"Résumé de la rumeur\", \"pourcentage_fiabilite\": \"75% (En négociations)\", \"image_url\": \"URL d'image pertinente\"}\n"
            "  ]\n"
            "}"
        )
        
        user_content = f"""
        Club phare : {club_phare}
        Équipe cible : {team_target or club_phare}
        Période analysée : "Récente"
        
        [DONNÉES WEB MERCATO GLOBAL] :
        {raw_global_data}
        
        [DONNÉES WEB MERCATO SPECIFIQUE {str(team_target).upper() if team_target else str(club_phare).upper()}] :
        {raw_team_data}
        """

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_content)
        ]
        
        info_mercato_liste = []
        try:
            # Appel au LLM en forçant le format JSON d'évitement de crash
            response = self.llm.invoke(messages, response_format={"type": "json_object"})
            parsed_mercato = json.loads(response.content)
            
            # On glisse l'objet complet structuré dans la liste pour le State
            info_mercato_liste.append(parsed_mercato)
            
        except Exception as e:
            print(f"[MercatoAgent Error] Échec du parsing de la revue des transferts : {e}")
            # Fallback basique pour ne pas bloquer le graphe
            info_mercato_liste.append({
                "mercato_global": [],
                "mercato_equipe": [{"joueur": "Archivage", "details": "Le moteur de veille continue d'analyser les signaux du mercato pour le club phare.", "pourcentage_fiabilite": "0%"}]
            })

        # 3. Envoi des données collectées dans le State
        return {
            "info_mercato": info_mercato_liste
        }