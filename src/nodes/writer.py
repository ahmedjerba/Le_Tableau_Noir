# src/nodes/writer_agent.py

from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from src.state import DigestState
from src.tools.agent_context_shared import create_groq_llm

class WriterAgentNode:
    def __init__(self):
        # Température très basse (0.2) pour garantir une mise en page stricte sans bavure
        self.llm = create_groq_llm(temperature=0.2)

    def __call__(self, state: DigestState) -> Dict[str, Any]:
        print("[WriterAgent] Rédaction de la revue de presse sportive 'Le Tableau Noir'...")

        # 1. Extraction sécurisée et alignement avec les vraies clés du State
        info_gen = state.get("info_general", [])[-1] if state.get("info_general") else {}
        info_mer = state.get("info_mercato", [])[-1] if state.get("info_mercato") else {}
        info_hist = state.get("info_histoire", [])[-1] if state.get("info_histoire") else {}
        info_stats = state.get("info_stats", [])[-1] if state.get("info_stats") else {}
        info_team = state.get("info_scoop_sur_equipe", [])[-1] if state.get("info_scoop_sur_equipe") else {}
        info_player = state.get("info_scoop_sur_joueur", [])[-1] if state.get("info_scoop_sur_joueur") else {}
        info_fun = state.get("info_funny", [])[-1] if state.get("info_funny") else {}

        # 2. Prompt journalistique adapté au traitement de dictionnaires de données
        system_prompt = (
    "Tu es le Rédacteur en Chef de la revue sportive prestigieuse 'Le Tableau Noir'.\n"
    "Ton rôle est de transformer des blocs de données JSON bruts, transmis par tes correspondants, "
    "en articles passionnants, fluides, analytiques et parfaitement rédigés. Tu ne dois JAMAIS afficher de résidus de format JSON "
    "(pas d'accolades, pas de clés textuelles comme 'recit' ou 'metrique' écrites brutes).\n\n"
    
    "⚠️ DIRECTIVES DE SÉCURITÉ ET DE FIABILITÉ ÉDITORIALE (STRICTES) :\n"
    "1. ANCRAGE TEMPOREL ACTUEL (2025/2026) : Nous sommes en 2026. Tu ne dois tolérer aucun anachronisme. Si les données évoquent des joueurs qui ont quitté le club depuis des années (ex: Benzema au Real Madrid), ignore ces noms obsolètes ou adapte la critique aux joueurs de l'effectif actuel de la saison en cours.\n"
    "2. INTERDICTION DE COMMENTER LES SITES WEB : Ne mentionne jamais le nom des sites sources ou des moteurs de recherche dans ton texte (ne dis pas 'L'Équipe propose une actualité...', 'Maxifoot partage sa passion' ou 'Selon Wikipédia'). Traduis cela immédiatement en jargon journalistique : 'Selon nos confrères de la presse spécialisée', 'D'après les échos des rédactions espagnoles', etc.\n"
    "3. GESTION DES DONNÉES VIDES OU FALLBACKS : Si un correspondant t'envoie un rapport vide ou une mention du type 'Calme plat' / 'Aucune info exclusive' / 'Indisponible', interdiction de l'écrire tel quel ou de dire 'Malheureusement nous n'avons pas d'infos'. À la place, utilise ton expertise pour contextualiser : explique pourquoi l'actualité est verrouillée ou calme en ce moment (ex: trêve internationale, langue de bois des joueurs, concentration maximale avant un grand match).\n"
    "4. PARALLÈLE HISTORIQUE COHÉRENT : Dans la rubrique 'La Machine à Remonter le Temps', le récit historique ou l'anecdote DOIT avoir un lien logique et direct avec le club phare traité. Ne parle pas du Barça ou d'un autre club rival pour illustrer l'histoire interne du club cible, sauf s'il s'agit d'une confrontation directe (Clasico, etc.).\n\n"
    
    "Respecte scrupuleusement la charte éditoriale suivante :\n"
    "- Structure claire avec des titres accrocheurs (H1, H2, H3), des listes à puces et l'utilisation du gras pour guider l'œil.\n"
    "- Intègre obligatoirement l'image d'archive historique présente dans les données sous la syntaxe : ![Description](URL).\n"
    "- Adopte un ton d'expert tactique, très immersif, incisif, parfois piquant ou romancé selon l'esprit de la rubrique.\n\n"
    
    "Ta revue doit obligatoirement être rédigée en français et contenir ces 7 rubriques exactes :\n"
    "1. 📰 LE ONZE TITULAIRE (Synthèse de l'actu globale européenne et focus situationnel du club phare)\n"
    "2. 🧮 LE PROF DE MATH (Décryptage data, statistiques avancées, analyses xG et animations tactiques)\n"
    "3. 💰 MONEY TIME (Le point complet sur les rumeurs mercato, montants évoqués et coulisses business)\n"
    "4. 🕵️‍♂️ JAMES BOND (Révélations exclusives sur l'ambiance des vestiaires et secrets d'équipe)\n"
    "5. 📸 PAPARAZZI SUR SCOOTER (Dernières déclarations croustillantes, coups d'éclat ou buzz autour de la star ciblée)\n"
    "6. ⏳ LA MACHINE À REMONTER LE TEMPS (Récit du parallèle historique ou de l'anecdote trouvée, en insistant sur l'année et le lien logique avec aujourd'hui)\n"
    "7. 🤪 LE ZAP DU FOOT (Les perles insolites, les déclarations lunaires de la semaine ou le troll bien senti sur le club)"
)

        # Injection des dictionnaires structurés
        user_content = f"""
        Voici la matière première récoltée sous format structuré pour le numéro de la semaine :
        
        [Données Le Onze Titulaire] : {info_gen}
        [Données Le Prof De Math] : {info_stats}
        [Données Money Time] : {info_mer}
        [Données James Bond] : {info_team}
        [Données Paparazzi Sur Scooter] : {info_player}
        [Données La Machine à Remonter le Temps] : {info_hist}
        [Données Le ZAP DU FOOT] : {info_fun}
        """

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_content)
        ]

        try:
            response = self.llm.invoke(messages)
            markdown_final = response.content
            status = "SUCCESS"
        except Exception as e:
            print(f"[WriterAgent Error] Échec de la synthèse finale : {e}")
            markdown_final = "# Le Tableau Noir\n\nErreur critique lors de l'assemblage de la revue de presse."
            status = "FAILED"

        return {
            "final_markdown": markdown_final,
            "status": status
        }