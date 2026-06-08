from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from src.state import DigestState
from src.tools.agent_context_shared import create_groq_llm

class WriterAgentNode:
    def __init__(self):
        self.llm = create_groq_llm(temperature=0.2)

    def __call__(self, state: DigestState) -> Dict[str, Any]:
        print("[WriterAgent] 📰 Assemblage final du magazine 'Le Tableau Noir'...")

        info_gen = state.get("info_general", [])[-1] if state.get("info_general") else {}
        info_stats = state.get("info_stats", [])[-1] if state.get("info_stats") else {}
        info_mer = state.get("info_mercato", [])[-1] if state.get("info_mercato") else {}
        
        # 🟢 EXTRACTION DEPUIS TA CLÉ DE STATE EXACTE
        info_club = state.get("info_club_specialiste", [])[-1] if state.get("info_club_specialiste") else {}
        
        info_hist = state.get("info_histoire", [])[-1] if state.get("info_histoire") else {}
        info_fun = state.get("info_funny", [])[-1] if state.get("info_funny") else {}

        system_prompt = (
            "Tu es le Rédacteur en Chef de la prestigieuse revue sportive 'Le Tableau Noir'.\n"
            "Ton rôle est de fusionner et de sublimer les chroniques prêtes au format Markdown envoyées par tes journalistes.\n"
            "Tu as interdiction absolue de laisser transparaître des accolades ou des clés de dictionnaire.\n\n"
            "Nous sommes en 2026. Élimine toute mention directe de sites web sources (Fbref, Wikipédia...) et utilise des tournures journalistiques nobles.\n\n"
            "Le magazine final doit obligatoirement être rédigé en français et contenir ces 6 rubriques unifiées :\n"
            "1. 📰 LE ONZE TITULAIRE (Actu générale européenne)\n"
            "2. 🧮 LE PROF DE MATH (Décryptage tactique et métriques xG/PPDA)\n"
            "3. 💰 MONEY TIME (Dossiers mercato et finances)\n"
            "4. 🕵️‍♂️ INSIDE VESTIAIRE (Les coulisses humaines et indiscrétions du club)\n"
            "5. ⏳ LA MACHINE À REMONTER LE TEMPS (Parallèle historique rétro et image d'archive)\n"
            "6. 🤪 LE ZAP DU FOOT (Les perles insolites et l'ironie de fin de numéro)"
        )

        user_content = f"""
        Voici les chroniques de la semaine à assembler :
        - [Le Onze Titulaire] : {info_gen.get('texte_redige', '')}
        - [Le Prof De Math] : {info_stats.get('texte_redige', '')}
        - [Money Time] : {info_mer.get('texte_redige', '')}
        - [Inside Vestiaire] : {info_club.get('texte_redige', '')}
        - [La Machine à Remonter le Temps] : {info_hist.get('texte_redige', '')}
        - [Le Zap du Foot] : {info_fun.get('texte_redige', '')}
        """

        try:
            response = self.llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_content)])
            markdown_final = response.content
            status = "SUCCESS"
        except Exception as e:
            print(f"[WriterAgent Error] Échec de l'assemblage : {e}")
            markdown_final = "# Le Tableau Noir\n\nErreur critique lors de la mise en page."
            status = "FAILED"

        return {"final_markdown": markdown_final, "status": status}