import json 
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage
from src.state import DigestState
from src.tools.agent_context_shared import resolve_primary_team, create_groq_llm

class FunnyAgentNode:
    def __init__(self):
        # Température un peu plus haute conservée pour garder la créativité et le piquant
        self.llm = create_groq_llm(temperature=0.6)
        
    def __call__(self, state: DigestState) -> Dict[str, Any]:
        print("[FunnyAgent] Génération de la dose d'insolence et de dérision...")
        
        # Récupération de l'équipe pour pouvoir glisser un petit tacle contextuel
        club_phare = resolve_primary_team(state)
        
        # PEAUFINAGE : On utilise directement la matière extraite par le GlobalContextAgent
        contexte_global = state.get("contexte_global", {})
        faits_semaine = ", ".join(contexte_global.get("faits_majeurs", []))
        scores_semaine = ", ".join(contexte_global.get("scores_marquants", []))
        
        system_prompt = (
            "Tu es le rédacteur satirique et sniper officiel du magazine 'Le Tableau Noir'. Ton style mélange l'insolence "
            "de 'So Foot' et le cynisme de 'Winamax Sport'.\n"
            "Ton rôle est d'apporter de l'ironie, du second degré, de pointer du doigt les absurdités, les déclarations chaotiques "
            "ou les flops de l'actualité récente du football mondial.\n\n"
            "Consignes de rédaction :\n"
            "1. Base-toi sur les faits réels et les scores fournis pour l'actualité de la semaine.\n"
            "2. Rédige un bloc d'humour incisif : quelques perles bien acérées sous forme de punchlines, suivies d'un petit troll ou d'une vame amicale "
            f"sur la situation ou l'attente autour du club '{club_phare}'.\n\n"
            "Tu dois obligatoirement répondre sous ce format JSON strict :\n"
            "{\n"
            "  \"data_brute\": {\n"
            "     \"sujet_trollé\": \"Le principal fait ou acteur visé cette semaine\",\n"
            "     \"degré_de_sel\": \"Un adjectif ironique (ex: Élevé, Extra-Dry, Mer Noire)\"\n"
            "  },\n"
            "  \"texte_redige\": \"Ton article satirique complet formaté en Markdown (titre, punchlines avec des puces, ton caustique)...\"\n"
            "}"
        )
        
        user_content = f"""
        Club favori de l'utilisateur : {club_phare}
        
        [ACTUALITÉ DU FOOTBALL MONDIAL CETTE SEMAINE] :
        - Faits marquants : {faits_semaine or "Aucun fait majeur signalé."}
        - Scores et chocs : {scores_semaine or "Pas de gros scores enregistrés."}
        """

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_content)
        ]
        
        info_funny_liste = []
        try:
            # Mode JSON strict activé sur Groq
            response = self.llm.invoke(messages, response_format={"type": "json_object"})
            parsed_funny = json.loads(response.content)
            
            # Injection des métadonnées pour harmoniser le State
            article_formate = {
                "metadata": {"source": "Satire / Zapping"},
                "data_brute": parsed_funny.get("data_brute", {}),
                # On s'assure d'encapsuler la rubrique proprement
                "texte_redige": f"### LE ZAP DU FOOT : L'insolence de la semaine\n\n{parsed_funny.get('texte_redige', '')}"
            }
            info_funny_liste.append(article_formate)
            
        except Exception as e:
            print(f"[FunnyAgent Error] Échec du parsing ou de la génération : {e}")
            info_funny_liste.append({
                "metadata": {"source": "Fallback"},
                "data_brute": {"sujet_trollé": "Néant", "degré_de_sel": "Neutre"},
                "texte_redige": "### LE ZAP DU FOOT : RAS\n\nLes joueurs ont été étonnamment professionnels cette semaine. Aucun tacle assassin sur les réseaux sociaux, aucun changement de coupe de cheveux suspect. On s'ennuie."
            })

        # Retourne la clé exacte attendue par notre nouveau state.py
        return {"info_funny": info_funny_liste}