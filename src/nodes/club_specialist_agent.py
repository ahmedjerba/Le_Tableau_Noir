import json 
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage
from src.state import DigestState
from src.tools.agent_context_shared import resolve_primary_team, create_groq_llm

class ScoopTeamAgentNode:
    def __init__(self):
        # Température basse (0.3) pour rester fidèle aux bruits de couloirs réels sans inventer de faux dramas
        self.llm = create_groq_llm(temperature=0.3)
        
    def __call__(self, state: DigestState) -> Dict[str, Any]:
        print("[ScoopTeamAgent] Infiltration dans les coulisses et l'intimité du vestiaire...")
        
        club_phare = resolve_primary_team(state)
        
        # 1. Extraction des données préparées en amont par les agents de contexte
        contexte_global = state.get("contexte_global", {})
        faits_mondiaux = ", ".join(contexte_global.get("faits_majeurs", []))
        
        contexte_equipe = state.get("contexte_equipe", {})
        actu_club = contexte_equipe.get("dernier_match_ou_actu_brûlante", "")
        coulisses_club = ", ".join(contexte_equipe.get("coulisses_mercato", []))
        climat_club = contexte_equipe.get("climat_interne", "")

        system_prompt = (
            "Tu es l'agent infiltré au cœur du club cible ({target}). Tu dois analyser l'actualité interne du club."

"Si l'équipe est en trêve ou qu'il n'y a pas d'actualité chaude de vestiaire, parle de la stratégie globale du club, de la gestion de ses infrastructures, de l'état de forme de ses internationaux en sélection, ou de la vision à long terme de sa direction."
            "Consignes de rédaction :\n"
            "1. Ne t'éparpille pas sur les statistiques tactiques, concentre-toi sur l'aspect humain, managérial et les indiscrétions.\n"
            f"2. Ton focus central et absolu doit être le club suivant : {club_phare}.\n"
            "3. Rédige une chronique immersive et piquante au format Markdown dans la clé 'texte_redige'. Prends un ton d'initié "
            "qui murmure les secrets du football à l'oreille de ses lecteurs.\n\n"
            "Tu devez obligatoirement répondre sous ce format JSON strict :\n"
            "{\n"
            "  \"data_brute\": {\n"
            "     \"ambiance_generale\": \"Un mot résumant le climat (ex: Électrique, Serein, Sous Haute Tension)\",\n"
            "     \"homme_cle_vestiaire\": \"Le joueur ou dirigeant au centre des discussions cette semaine\"\n"
            "  },\n"
            "  \"texte_redige\": \"Ton grand article d'investigation complet en Markdown (avec titres, révélations sous forme de paragraphes rédigés)...\"\n"
            "}"
        )
        
        user_content = f"""
        Club cible de l'utilisateur : {club_phare}
        
        [RAPPORTS DE TERRAIN SUR LE CLUB] :
        - Actualité chaude : {actu_club}
        - Coulisses et mouvements : {coulisses_club}
        - Climat interne du groupe : {climat_club}
        
        [BRUITS DE COULOIRS EUROPÉENS] :
        - Grandes tendances de la semaine : {faits_mondiaux or "Pas de crise majeure globale signalée."}
        """

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_content)
        ]
        
        info_scoop_team_liste = []
        try:
            # Invocation avec format de sortie JSON Object structuré
            response = self.llm.invoke(messages, response_format={"type": "json_object"})
            parsed_scoops = json.loads(response.content)
            
            # Structuration finale avec encapsulation de la rubrique
            article_formate = {
                "metadata": {
                    "source": "Infiltré Vestiaire",
                    "club_espionne": club_phare
                },
                "data_brute": parsed_scoops.get("data_brute", {}),
                # Intégration du titre de la rubrique d'investigation
                "texte_redige": f"### INSIDE : Les secrets du vestiaire\n\n{parsed_scoops.get('texte_redige', '')}"
            }
            info_scoop_team_liste.append(article_formate)
            
        except Exception as e:
            print(f"[ScoopTeamAgent Error] Échec critique du parsing des révélations : {e}")
            info_scoop_team_liste.append({
                "metadata": {"source": "Fallback"},
                "data_brute": {"ambiance_generale": "Calme", "homme_cle_vestiaire": "Néant"},
                "texte_redige": f"### INSIDE : Les secrets du vestiaire\n\nLes verrous des vestiaires de {club_phare} ont tenu bon cette semaine. Les causeries d'avant-match et les secrets de couloir restent bien gardés au centre d'entraînement."
            })

        # Renvoi de la clé synchronisée attendue dans state.py
        # Fin de la méthode __call__ de ton agent spécialiste :
        return {
            "info_scoop_team": info_scoop_team_liste
        }