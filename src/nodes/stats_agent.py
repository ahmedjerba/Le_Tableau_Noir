import json 
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage
from src.state import DigestState
from src.tools.web_search import web_search
from src.tools.agent_context_shared import resolve_primary_team, build_football_query, create_groq_llm

class StatsAgentNode:
    def __init__(self):
        # Température très basse (0.1) conservée pour garantir une rigueur mathématique absolue
        self.llm = create_groq_llm(temperature=0.1)
        
    def __call__(self, state: DigestState) -> Dict[str, Any]:
        print("[StatsAgent] Extraction des métriques avancées et structures de performance...")
        
        club_phare = resolve_primary_team(state)
        
        # 1. Exploitation du contexte global déjà collecté pour la tendance de fond
        contexte_global = state.get("contexte_global", {})
        faits_semaine = ", ".join(contexte_global.get("faits_majeurs", []))
        scores_semaine = ", ".join(contexte_global.get("scores_marquants", []))

        # 2. Recherche ciblée exclusive sur la data pointue du club phare (7 derniers jours automatique)
        sites_stats = ["theanalyst.com", "fbref.com", "understat.com", "sofascore.com", "whoscored.com"]
        print(f"[StatsAgent] Analyse des rapports métriques avancés pour : {club_phare}...")
        query_team = build_football_query("metrics xG performance PPDA", club_phare)
        
        raw_team_data = web_search.invoke({
            "query": query_team, 
            "target_sites": sites_stats, 
            "max_results": 6
        })
        
        system_prompt = (
    "Tu es l'expert data de la rédaction. Regarde les données de recherche web fournies :"

"Si les données contiennent des statistiques de matchs récents : Décrypte les performances (xG, pressings, circuits de passes)."

"Si les données sont vides ou qu'aucun match n'a lieu : Bascule immédiatement en mode 'Masterclass Tactique'. Choisis un concept mathématique ou tactique du football (ex: le calcul des Expected Goals, l'évolution du rôle de Sentinelle, l'impact du PPDA) et explique-le de manière pédagogique et passionnante pour les lecteurs."
    "⚠️ CONSIGNE DE SÉCURITÉ DE FORMATAGE :\n"
    "Tu dois obligatoirement répondre sous la forme d'un objet JSON strict avec ces deux clés :\n"
    "1. 'data_brute': Un dictionnaire d'indicateurs.\n"
    "2. 'texte_redige': Une chaîne de caractères contenant ta chronique rédigée en Markdown.\n"
    "ATTENTION : Pour que le JSON soit valide, tu dois impérativement échapper chaque saut de ligne par '\\n' et ne pas mettre de caractères de contrôle bruts.\n\n"
    
    "Si la recherche web ne renvoie aucune métrique fraîche (période calme), utilise ton expertise pour analyser "
    "les grandes tendances tactiques globales de la saison 2025/2026 qui vient de s'achever (ex: l'évolution du pressing haut en Europe)."
)
        
        user_content = f"""
        Club cible prioritaire : {club_phare}
        
        [CONTEXTE DE L'ACTUALITÉ GÉNÉRALE DE LA SEMAINE] :
        - Événements majeurs : {faits_semaine or "Aucun fait marquant."}
        - Résultats récents : {scores_semaine or "Pas de scores spécifiques."}
        
        [DONNÉES BRUTES DE TRACKING WEB POUR {str(club_phare).upper()}] :
        {raw_team_data}
        """

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_content)
        ]
        
        info_stats_liste = []
        try:
            # Invocation avec format de sortie JSON Object forcé
            response = self.llm.invoke(messages, response_format={"type": "json_object"})
            parsed_data = json.loads(response.content)
            
            # Structuration finale et harmonisation pour l'assemblage du Writer
            article_formate = {
                "metadata": {
                    "source": "Opta / Data Engine",
                    "club_analyse": club_phare
                },
                "data_brute": parsed_data.get("data_brute", {}),
                # Intégration directe du titre de la rubrique
                "texte_redige": f"### ANALYSE DATA : Le rapport de performance\n\n{parsed_data.get('texte_redige', '')}"
            }
            info_stats_liste.append(article_formate)
            
        except Exception as e:
            print(f"[StatsAgent Error] Échec du parsing ou du traitement métrique : {e}")
            info_stats_liste.append({
                "metadata": {"source": "Fallback"},
                "data_brute": {"metrique_cle_semaine": "Indisponible", "valeur": "N/A"},
                "texte_redige": "### ANALYSE DATA : Rapport en attente\n\nLes serveurs de tracking ou les API de relevés tactiques n'ont pas renvoyé de métriques aberrantes ou d'anomalies notables cette semaine pour cette configuration."
            })

        # Renvoi de la clé synchronisée avec ton state.py
        return {
            "info_stats": info_stats_liste
        }