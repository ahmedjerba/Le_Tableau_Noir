from typing import Dict, Any, List
from src.state import DigestState

class ValidatorAgentNode:
    def __init__(self):
        pass

    def __call__(self, state: DigestState) -> Dict[str, Any]:
        print("\n[ValidatorAgent] 🔍 Analyse de conformité des rapports de la rédaction...")
        retry_list = []

        def est_invalide(cle_state: str, fallback_keyword: str) -> bool:
            liste_rubrique = state.get(cle_state, [])
            if not liste_rubrique:
                return True
            dernier_item = liste_rubrique[-1] if isinstance(liste_rubrique[-1], dict) else {}
            texte_article = str(dernier_item.get("texte_redige", ""))
            return not texte_article or fallback_keyword.lower() in texte_article.lower()

        if est_invalide("info_general", "Les affaires courantes"):
            retry_list.append("general_agent")

        if est_invalide("info_stats", "Rapport en attente"):
            retry_list.append("stats_agent")

        if est_invalide("info_mercato", "Calme plat dans les bureaux"):
            retry_list.append("mercato_agent")

        # 🟢 VALIDATION DE LA CLÉ EXACTE DE TON STATE
        #if est_invalide("info_club_specialiste", "Les verrous des vestiaires"):
            #print("⚠️ [Validator] La rubrique Inside Vestiaire (info_club_specialiste) est absente ou en fallback.")
           # retry_list.append("scoop_team_agent")

        if est_invalide("info_histoire", "Fallback"):
            retry_list.append("histoire_agent")

        if est_invalide("info_funny", "Les joueurs ont été étonnamment professionnels"):
            retry_list.append("funny_agent")

        if retry_list:
            print(f"❌ [Validator] Validation ÉCHOUÉE pour : {retry_list}\n")
            return {"validation_status": "RETRY", "retry_agents": retry_list}
        
        print("✅ [Validator] Validation RÉUSSIE. Structure conforme !\n")
        return {"validation_status": "APPROVED", "retry_agents": []}