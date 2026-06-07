# src/nodes/planner.py

import json
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from src.state import DigestState
from src.tools.agent_context_shared import create_groq_llm


class PlannerNode:
    def __init__(self):
        # Température basse pour garantir le respect strict du schéma JSON
        self.model = create_groq_llm(temperature=0.3)

    def __call__(self, state: DigestState) -> Dict[str, Any]:
        print("\n[PlannerNode] Initialisation du plan de rédaction et répartition des tâches...")
        
        preferences = state.get("user_preferences", {})
        teams = preferences.get("teams", [])
        players = preferences.get("players", [])
        leagues = preferences.get("leagues", [])
        time_window = state.get("time_window", "les derniers jours")
        
        # Fallbacks de sécurité pour le prompt
        if not teams:
            teams = ["les équipes majeures du football mondial"]
        if not players:
            players = ["les joueurs les plus en vue du moment"]
        if not leagues:
            leagues = ["les championnats les plus suivis du moment"]

        club_phare = teams[0] if teams else ""
        joueur_star = players[0] if players else ""
        
        system_prompt = (
    "Tu es le Directeur de la Rédaction de 'Le Tableau Noir', un magazine de football ultra-spécialisé.\n"
    "Ton rôle est de préparer le plan de recherche pour tes 7 journalistes spécialisés (les agents).\n"
    "Tu dois analyser les goûts de l'abonné et définir les titres de chapitres ainsi que les angles d'attaque.\n\n"

    "⚠️ RÈGLE D'OR ABSOLUE POUR LA CLÉ 'target' :\n"
    "Quand tu définis la valeur de 'target' pour les agents qui se focalisent sur l'équipe (comme stats_agent, scoop_team_agent, mercato_agent), tu dois IMPÉRATIVEMENT mettre un NOM DE CLUB DE FOOTBALL RÉEL ET PRÉCIS (ex: 'Real Madrid', 'Paris Saint-Germain', 'FC Barcelone', 'Manchester City').\n"
    "Il est STRICTEMENT INTERDIT de mettre un nom de compétition, de ligue ou de pays dans la clé 'target' (BANNIR ABSOLUMENT : 'La Liga', 'Ligue 1', 'Champions League', 'Premier League', 'Espagne'). Si l'abonné aime un championnat, sélectionne l'un des clubs majeurs de ce championnat.\n\n"

    "Tu dois IMPÉRATIVEMENT cibler ces 7 types d'agents exacts dans tes missions :\n"
    "- 'general_agent' : Actu foot mondiale (3 news) et club phare (2 news)\n"
    "- 'stats_agent' : Analyses de données et statistiques avancées\n"
    "- 'mercato_agent' : Transferts, rumeurs globales et business\n"
    "- 'scoop_team_agent' : Secrets de vestiaire et coulisses de l'équipe\n"
    "- 'scoop_player_agent' : Révélations et focus sur un joueur star\n"
    "- 'historical_agent' : Parallèle historique rétro\n"
    "- 'funny_agent' : L'anecdote ou mème insolite global\n\n"
    
    "Tu dois obligatoirement répondre sous la forme d'un objet JSON strict contenant exactement ces deux clés :\n"
    "1. 'sections_to_write': Une liste de chaînes représentant les titres des rubriques.\n"
    "2. 'planned_sections': Une liste d'objets décrivant les missions. Chaque objet doit avoir les clés 'agent_type', 'target' et 'instructions'.\n\n"
    
    "Exemple de format JSON attendu :\n"
    "{\n"
    "  \"sections_to_write\": [\"Le Onze Titulaire\", \"Le Prof De Math\", \"Money Time\", \"James Bond\", \"Paparazzi Sur Scooter\", \"La Machine à Remonter le Temps\", \"Le ZAP DU FOOT\"],\n"
    "  \"planned_sections\": [\n"
    "    {\"agent_type\": \"stats_agent\", \"target\": \"Real Madrid\", \"instructions\": \"Extraire les stats du match le plus récent du club\"},\n"
    "    {\"agent_type\": \"mercato_agent\", \"target\": \"Real Madrid\", \"instructions\": \"Vérifier les mouvements du marché mondial et les rumeurs du club\"}\n"
    "  ]\n"
    "}"
)
        
        user_content = f"""
        Profil de l'abonné :
        - Équipes favorites : {teams}
        - Joueurs suivis : {players}
        - Championnats observés : {leagues}
        - Période temporelle : {time_window}
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_content)
        ]
        
        try:
            response = self.model.invoke(messages, response_format={"type": "json_object"})
            plan_data = json.loads(response.content)
            
            # 🛡️ SECURITÉ ANTI-COMPÉTITION ("La Liga", etc.)
            compétitions_interdites = ["la liga", "ligue 1", "premier league", "champions league", "serie a", "liga", "champions"]
            
            # On parcourt les sections générées par le LLM pour corriger les cibles erronées
            if "planned_sections" in plan_data:
                for section in plan_data["planned_sections"]:
                    target_value = section.get("target", "")
                    # Si le LLM a mis une compétition au lieu d'un club, on force un club d'ancrage
                    if str(target_value).lower() in compétitions_interdites or len(str(target_value)) < 4:
                        section["target"] = "Real Madrid"

            # Extraction dynamique du club phare pour synchroniser le state global
            club_detecte = None
            if "planned_sections" in plan_data:
                for section in plan_data["planned_sections"]:
                    if section.get("agent_type") in ["stats_agent", "scoop_team_agent", "mercato_agent"]:
                        val = section.get("target", "")
                        if val.lower() not in compétitions_interdites and len(val) >= 4:
                            club_detecte = val
                            break

            # Si on a détecté un vrai club dans le JSON, on l'utilise, sinon on prend la variable ou "Real Madrid"
            current_club = club_detecte or club_phare or "Real Madrid"
            
            # Injection et écrasement propre dans plan_data
            plan_data["club_phare"] = current_club
            plan_data["target_team"] = current_club
            
            if joueur_star:
                plan_data["joueur_star"] = joueur_star
                plan_data["target_player"] = joueur_star
                
            print(f"✅ [PlannerNode] Planification générée. Club synchronisé : '{current_club}'")
            
        except Exception as e:
            print(f"❌ Erreur lors de la génération du plan : {e}")
            # Fallback robuste aligné sur la structure
            fallback_club = club_phare or "Real Madrid"
            plan_data = {
                "sections_to_write": ["Le Onze Titulaire", "Le Prof De Math", "Money Time", "James Bond", "Paparazzi Sur Scooter", "La Machine à Remonter le Temps", "Le ZAP DU FOOT"],
                "planned_sections": [
                    {"agent_type": "general_agent", "target": "football mondial", "instructions": "Actualité majeure du football mondial"},
                    {"agent_type": "stats_agent", "target": fallback_club, "instructions": "Dernières statistiques tactiques du club phare"}
                ]
            }
            plan_data["club_phare"] = fallback_club
            plan_data["target_team"] = fallback_club
            if joueur_star:
                plan_data["joueur_star"] = joueur_star
                plan_data["target_player"] = joueur_star
            
        # LE RETURN ACCESSIBLE PAR LE TRY ET LE EXCEPT
        return {
            "sections_to_write": plan_data.get("sections_to_write", []),
            "planned_sections": plan_data.get("planned_sections", []),
            "club_phare": plan_data.get("club_phare", club_phare or "Real Madrid"),
            "target_team": plan_data.get("target_team", club_phare or "Real Madrid"),
            "joueur_star": plan_data.get("joueur_star", joueur_star),
            "target_player": plan_data.get("target_player", joueur_star),
            "status": "collecting"
        }