import json
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from src.state import DigestState
from src.tools.agent_context_shared import create_groq_llm

class PlannerNode:
    def __init__(self):
        self.model = create_groq_llm(temperature=0.3)

    def __call__(self, state: DigestState) -> Dict[str, Any]:
        print("\n[PlannerNode] Initialisation du plan de rédaction et répartition des tâches...")
        
        preferences = state.get("user_preferences", {})
        teams = preferences.get("teams", [])
        players = preferences.get("players", [])
        leagues = preferences.get("leagues", [])
        time_window = state.get("time_window", "les derniers jours")
        
        if not teams:
            teams = ["les équipes majeures du football mondial"]

        club_phare = teams[0]
        
        system_prompt = (
            "Tu es le Directeur de la Rédaction de 'Le Tableau Noir', un magazine de football ultra-spécialisé.\n"
            "Ton rôle est de préparer le plan de recherche pour tes 6 journalistes spécialisés (les agents).\n\n"
            "⚠️ RÈGLE D'OR ABSOLUE POUR LA CLÉ 'target' :\n"
            "Quand tu définis la valeur de 'target' pour les agents qui se focalisent sur l'équipe (comme stats_agent, info_club_specialiste, mercato_agent), tu dois IMPÉRATIVEMENT mettre un NOM DE CLUB DE FOOTBALL RÉEL ET PRÉCIS (ex: 'Real Madrid', 'Paris Saint-Germain').\n\n"
            "Tu dois IMPÉRATIVEMENT cibler ces 6 types d'agents exacts dans tes missions :\n"
            "- 'general_agent' : Actu foot mondiale et focus sur le club principal\n"
            "- 'stats_agent' : Analyses de données et statistiques avancées (xG, PPDA)\n"
            "- 'mercato_agent' : Transferts, business et rumeurs de couloir financières\n"
            "- 'info_club_specialiste' : Secrets de vestiaire, gestion humaine et coulisses exclusives du club principal\n"
            "- 'historical_agent' : Parallèle historique rétro et anecdotes légendaires\n"
            "- 'funny_agent' : Perles insolites, mèmes et angle satirique\n\n"
            "Tu devez obligatoirement répondre sous la forme d'un objet JSON strict contenant exactement ces deux clés :\n"
            "1. 'sections_to_write': Une liste de chaînes représentant les 6 titres des rubriques.\n"
            "2. 'planned_sections': Une liste d'objets décrivant les missions. Chaque objet doit avoir les clés 'agent_type', 'target' et 'instructions'.\n\n"
            "Exemple de format JSON attendu :\n"
            "{\n"
            "  \"sections_to_write\": [\"Le Onze Titulaire\", \"Le Prof De Math\", \"Money Time\", \"Inside Vestiaire\", \"La Machine à Remonter le Temps\", \"Le ZAP DU FOOT\"],\n"
            "  \"planned_sections\": [\
                n"
            "     {\"agent_type\": \"info_club_specialiste\", \"target\": \"Real Madrid\", \"instructions\": \"Enquêter sur l'ambiance du vestiaire et les retours de blessure.\"}\n"
            "  ]\n"
            "}\n\n"
            "RÈGLE DE DISTRIBUTION :\n"
"- Pour general_agent, stats_agent, mercato_agent : la valeur de 'target' doit TOUJOURS être 'Football Mondial' ou 'Europe'.\n"
"- Uniquement pour scoop_team_agent : la valeur de 'target' doit être le club phare (ex: Real Madrid)."
        )
        
        user_content = f"""
        Profil de l'abonné :
        - Équipes favorites : {teams}
        - Joueurs suivis : {players}
        - Championnats observés : {leagues}
        - Période temporelle : {time_window}
        """
        
        try:
            response = self.model.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_content)], response_format={"type": "json_object"})
            plan_data = json.loads(response.content)
            
            competitions_interdites = ["la liga", "ligue 1", "premier league", "champions league", "serie a", "liga", "champions", "bundesliga"]
            if "planned_sections" in plan_data:
                for section in plan_data["planned_sections"]:
                    if str(section.get("target", "")).lower() in competitions_interdites:
                        section["target"] = club_phare if club_phare not in competitions_interdites else "Real Madrid"
                        
        except Exception as e:
            print(f"❌ Erreur lors de la génération du plan : {e}")
            plan_data = {
                "sections_to_write": ["Le Onze Titulaire", "Le Prof De Math", "Money Time", "Inside Vestiaire", "La Machine à Remonter le Temps", "Le ZAP DU FOOT"],
                "planned_sections": [
                    {"agent_type": "general_agent", "target": "football mondial", "instructions": "Actualité majeure"},
                    {"agent_type": "info_club_specialiste", "target": club_phare, "instructions": "Coulisses du club"}
                ]
            }
            
        return {
            "sections_to_write": plan_data.get("sections_to_write", []),
            "planned_sections": plan_data.get("planned_sections", []),
            "status": "collecting"
        }