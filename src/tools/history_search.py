import json
import wikipedia
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_community.utilities import WikipediaAPIWrapper
from typing import List, Dict, Any
from src.tools.agent_context_shared import create_groq_llm

# Configuration du User-Agent requise par la politique de Wikipedia
wikipedia.set_user_agent("LeTableauNoirBot/1.0 (contact: ahmedmustafajrad@gmail.com)")

def generate_archive_search_queries(recent_context: str) -> str:
    model = create_groq_llm(temperature=0.3)
    
    prompt = (
        "Tu es un historien du football mondial et un expert en recherche Wikipedia.\n"
        "À partir du contexte fourni, identifie le phénomène ou le scénario global de l'actualité récente, "
        "puis transforme-le en une requête Wikipedia ultra-courte.\n"
        "Contraintes obligatoires : 2 à 4 mots maximum, uniquement en français, le premier mot doit être 'football' ou 'foot', "
        "sans guillemets, sans ponctuation superflue, sans commentaire.\n"
        "Supprime toute restriction liée à une équipe spécifique : la requête doit viser l'événement historique mondial "
        "le plus marquant qui partage le même scénario.\n"
        "La requête doit cibler un événement ou un record précis, par exemple : 'football remontada barcelone', "
        "'foot grece euro 2004', 'football invincibles arsenal'.\n"
        "Réponds uniquement par la requête finale, sans texte additionnel."
    )
    
    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=recent_context)
    ]
    response = model.invoke(messages)
    return response.content.strip()

def search_historical_football_facts(recent_context: str) -> List[Dict[str, Any]]:
    """Interroge Wikipedia, analyse le résultat, et extrait une pépite historique structurée."""
    search_query = generate_archive_search_queries(recent_context)
    print(f"[History Search Wikipedia] Requête générée : '{search_query}'")
    
    search = WikipediaAPIWrapper(lang="fr", top_k_results=3, doc_content_chars_max=5000)
    
    try:
        wiki_results = search.run(search_query)
    except Exception as e:
        print(f"⚠️ Erreur lors de la recherche Wikipedia : {e}")
        wiki_results = ""
    
    llm = create_groq_llm(temperature=0.2)
    
    # Récriture du prompt pour exiger du JSON strict
    analysis_prompt = (
        "Tu es l'archiviste en chef du magazine 'Le Tableau Noir'.\n"
        "Parmi les données encyclopédiques de Wikipedia fournies, extrais la pépite historique la plus fascinante, "
        "l'anecdote oubliée ou le précédent le plus marquant qui fait directement écho au CONTEXTE ou au SCÉNARIO actuel.\n"
        "Si les résultats Wikipedia sont vides ou hors-sujet, utilise ta propre immense culture historique pour proposer un parallèle mythique.\n\n"
        "Rédige un compte-rendu historique captivant, romancé mais 100% vrai, en montrant subtilement le parallèle avec aujourd'hui.\n\n"
        "Tu dois obligatoirement répondre sous ce format JSON strict :\n"
        "{\n"
        "  \"titre_anecdote\": \"Le titre marquant de l'histoire (ex: Le hold-up parfait de la Grèce en 2004)\",\n"
        "  \"annee\": \"Année ou époque exacte (ex: 2004)\",\n"
        "  \"recit\": \"Ton texte narratif complet et captivant ici...\",\n"
        "  \"parallele_actuel\": \"Explication courte de pourquoi cela ressemble à la situation actuelle.\"\n"
        "}"
    )
    
    user_content = f"""
    Détails du contexte actuel : {recent_context}
    Résultats de la recherche historique sur Wikipedia : {wiki_results or 'Aucun résultat exploitable'}
    """
    
    messages = [
        SystemMessage(content=analysis_prompt),
        HumanMessage(content=user_content)
    ]
    
    try:
        # On force la réponse au format JSON pour éviter les crashs de chaîne
        response = llm.invoke(messages, response_format={"type": "json_object"})
        parsed_history = json.loads(response.content)
        
        # On conserve ton fallback d'image par défaut pour l'instant
        parsed_history["image_archive_url"] = "https://images.unsplash.com/photo-1508098682722-e99c43a406b2"
        return [parsed_history]
        
    except Exception as e:
        print(f"[History Analysis Error] Échec du parsing JSON de l'archiviste : {e}")
        return [{
            "titre_anecdote": "Parallèle historique",
            "annee": "Histoire",
            "recit": "L'histoire du football regorge de scénarios légendaires qui font étrangement écho aux dynamiques de l'actualité récente.",
            "parallele_actuel": "Connexion en cours d'analyse.",
            "image_archive_url": "https://images.unsplash.com/photo-1508098682722-e99c43a406b2"
        }]