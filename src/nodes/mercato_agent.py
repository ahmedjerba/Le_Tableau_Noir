# src/nodes/mercato_agent.py

from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from src.state import DigestState
from src.tools.agent_context_shared import create_groq_llm
from src.tools.web_search import web_search  # Aligne sur le nom exact de ton outil
import json

class MercatoAgentNode:
    def __init__(self):
        # Température un poil plus haute pour capter le ton "insider / rumeurs" du mercato
        self.model = create_groq_llm(temperature=0.6)

    def __call__(self, state: DigestState) -> Dict[str, Any]:
        print("[MercatoAgent] Analyse fine du marché des transferts et rumeurs globales...")

        # 1. Requête 100% orientée sur les blockbusters mondiaux du moment
        query_recherche = "football mercato rumeurs transferts officiels juin 2026"
        
        try:
            search_results = web_search.invoke({"query": query_recherche,"max_results": 5})
        except Exception as e:
            print(f"[MercatoAgent] Erreur recherche web: {e}")
            search_results = "Aucun résultat mercato récent sur le web."

        # 2. Prompt exigeant un angle global et interdisant le focus Real Madrid
        system_prompt = (
            "Tu es le spécialiste Business et Transferts. Analyse les données textuelles fournies. Interdiction d'inventer des rumeurs si le contexte est vide."

"Si le marché des transferts est fermé ou calme, oriente ta chronique sur l'économie du football : analyse la santé financière d'un grand championnat, l'impact des droits TV, ou le fonctionnement du marché des agents de joueurs."
            
            "⚠️ DIRECTIVE DE SÉCURITÉ FORMAT JSON :\n"
            "Tu dois impérativement répondre sous la forme d'un objet JSON strict contenant exactement ces deux clés :\n"
            "1. 'data_brute': Un dictionnaire contenant les noms des joueurs et clubs au cœur des rumeurs.\n"
            "2. 'texte_redige': Ta chronique complète rédigée en Markdown (sans afficher le titre global H1).\n"
            "ATTENTION : Échappe obligatoirement chaque saut de ligne avec '\\n' pour éviter de briser la structure du JSON.\n\n"
            
            "⚠️ CAS DE TRÊVE CALME (FALLBACK) :\n"
            "Si les news du jour sont minces, analyse les grandes tendances financières de ce début de mercato 2026 "
            "(ex: l'impact du fair-play financier sur les cadors européens ou les profils les plus recherchés cet été)."
            "⚠️ ATTENTION IMPÉRATIVE SUR LA DATE :\n"
"Nous sommes en JUIN 2026. Tu as interdiction absolue de parler de Neymar au PSG/Barça, de Aubameyang ou de Paul Pogba à Manchester United. "
"Ce sont des informations obsolètes de 2022. Base-toi UNIQUEMENT sur les cracks actuels de 2026 (ex: le marché des jeunes talents, les fins de contrat de juin 2026, l'Arabie Saoudite ou la Premier League)."
        )

        user_content = f"""
        Données fraîches du web concernant le marché des transferts :
        {search_results}
        
        Période : {state.get('time_window', 'cette semaine')} (Juin 2026)
        """

        try:
            response = self.model.invoke(
                [SystemMessage(content=system_prompt), HumanMessage(content=user_content)],
                response_format={"type": "json_object"}
            )
            result_json = json.loads(response.content)
            
        except Exception as e:
            print(f"[MercatoAgent Error] Échec de la génération ou du parsing JSON : {e}")
            # Repli propre et structuré en cas de raté
            result_json = {
                "data_brute": {"status": "fallback_mercato_global"},
                "texte_redige": (
                    "## JOURNAL DES TRANSFERTS : LES GRANDES MANŒUVRES ESTIVALES\\n\\n"
                    "Le marché européen entre dans sa phase d'ébullition en ce début de mois de juin 2026. "
                    "Avec l'ouverture officielle des fenêtres d'enregistrement, les directeurs sportifs des quatre coins du continent "
                    "activent leurs réseaux pour sécuriser les signatures prioritaires avant la reprise des entraînements."
                )
            }

        # 3. Retour aligné sur le canal d'accumulation du State
        return {
            "info_mercato": [
                {
                    "metadata": {"source": "Radar Mercato Global", "date": "Juin 2026"},
                    "data_brute": result_json.get("data_brute", {}),
                    "texte_redige": result_json.get("texte_redige", "")
                }
            ]
        }