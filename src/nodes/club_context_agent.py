import json
from langchain_core.messages import SystemMessage, HumanMessage
from src.tools.agent_context_shared import create_groq_llm
from src.tools.web_search import web_search
from src.state import DigestState

def context_club_node(state: DigestState) -> dict:
    """
    Nœud initial de la branche Club. Il isole et verrouille l'actualité 
    brûlante de l'équipe ciblée sur les 7 derniers jours.
    """
    # Récupération de l'équipe cible depuis le State
    target_team = state.get("team", "Real Madrid")
    print(f"🏟️ [ContextClubAgent] Début du scan exclusif sur le club : {target_team}...")
    
    # 1. Recherche DuckDuckGo ciblée (l'outil applique déjà le filtre des 7 derniers jours)
    search_query = f"{target_team} actualité mercato résultats vestiaire"
    search_data = web_search.invoke({"query": search_query, "max_results": 8})
    web_results = search_data.get("results", [])
    
    # 2. Préparation du modèle Groq en mode JSON strict
    llm = create_groq_llm(temperature=0.2)
    
    system_prompt = (
        f"Tu es le Correspondant Permanent et Chef de Bureau dédié à l'actualité du club : {target_team}.\n"
        "Ta mission est de trier les notes brutes du web pour en extraire l'état de forme et les coulisses de l'équipe cette semaine.\n\n"
        "Consignes impératives :\n"
        "1. Synthétise les dernières rumeurs de transferts ou officialisations internes au club.\n"
        "2. Détecte l'ambiance du vestiaire (déclarations du coach, tensions, prolongations de contrat).\n"
        "3. Reste STRICTEMENT concentré sur ce club. Ne t'éparpille pas sur le reste du championnat.\n\n"
        "Tu dois obligatoirement répondre sous ce format JSON strict :\n"
        "{\n"
        f"  \"club\": \"{target_team}\",\n"
        "  \"dernier_match_ou_actu_brûlante\": \"Résumé rapide du dernier fait saillant ou match de l'équipe\",\n"
        "  \"coulisses_mercato\": [\n"
        "    \"Première info transfert/contrat liée au club...\",\n"
        "    \"Deuxième info transfert/contrat liée au club...\"\n"
        "  ],\n"
        "  \"climat_interne\": \"État d'esprit du groupe, déclass du coach ou humeur des supporters cette semaine\"\n"
        "}"
    )
    
    user_content = f"""
    Notes de recherche terrain (Web) de la semaine pour {target_team} :
    ----------------------------------------------------------------
    {json.dumps(web_results, ensure_ascii=False, indent=2) if web_results else "Aucune donnée récente trouvée pour ce club."}
    ----------------------------------------------------------------
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_content)
    ]
    
    try:
        # Groq force la sortie au format JSON pour alimenter proprement l'agent spécialiste juste après
        response = llm.invoke(messages, response_format={"type": "json_object"})
        parsed_club_context = json.loads(response.content)
        
        print(f"✅ [ContextClubAgent] Contexte de l'équipe {target_team} verrouillé.")
        return {"contexte_equipe": parsed_club_context}
        
    except Exception as e:
        print(f"❌ [ContextClubAgent Error] Échec du parsing JSON pour le club {target_team} : {e}")
        # Sécurité pour ne pas bloquer le flux de la Branche C
        return {
            "contexte_equipe": {
                "club": target_team,
                "dernier_match_ou_actu_brûlante": "Données du club en cours d'actualisation.",
                "coulisses_mercato": ["Rumeurs de transition estivale."],
                "climat_interne": "Le club prépare ses prochains mouvements dans la discrétion."
            }
        }