from datetime import datetime
from duckduckgo_search import DDGS
from langchain_core.tools import tool
from typing import List, Union

@tool
def web_search(query: str, target_sites: Union[List[str], str] = None, max_results: int = 8) -> dict:
    """
    Effectue une recherche sur le web via DuckDuckGo pour obtenir les dernières infos du football.
    Filtre STRICTEMENT les résultats sur la dernière semaine glissante par rapport à l'exécution.
    Prend en charge les sites français et internationaux (Marca, The Athletic, Sky Sports, etc.).
    """
    # Récupération dynamique de l'année et du mois actuels
    now = datetime.now()
    current_year = now.strftime("%Y")      # Donne '2026' dynamiquement
    current_month_year = now.strftime("%B %Y") # Donne 'June 2026' ou 'Juin 2026'
    
    # On injecte dynamiquement l'année en cours si elle n'est pas précisée
    if current_year not in query:
        optimized_query = f"{query} {current_year}"
    else:
        optimized_query = query

    print(f"🕒 [WebSearch DDG] Date système détectée : {now.strftime('%d/%m/%Y')} ➔ Recherche sur les 7 derniers jours.")

    is_international = False
    if target_sites:
        if isinstance(target_sites, str):
            sites_list = [s.strip().lower() for s in target_sites.split(",") if s.strip()]
        else:
            sites_list = [str(s).strip().lower() for s in target_sites if str(s).strip()]
            
        if sites_list:
            international_extensions = [".com", ".es", ".it", ".co.uk", ".de", ".co", ".net"]
            if any(any(ext in site for ext in international_extensions) for site in sites_list):
                is_international = True
                
            filter_parts = [f"site:{site}" for site in sites_list]
            site_filter = " (" + " OR ".join(filter_parts) + ")"
            optimized_query = f"{optimized_query}{site_filter}"
            print(f"🌐 [WebSearch DDG] Mode Multi-Sites ({'International' if is_international else 'Français'}) ➔ {len(sites_list)} sources ciblées.")
    else:
        print(f"🌐 [WebSearch DDG] Mode Global ➔ Recherche générale pour : '{optimized_query}'")

    try:
        results = []
        current_region = "wt-wt" if is_international else "fr-fr"
        
        with DDGS() as ddgs:
            # timelimit="w" force DuckDuckGo à ne chercher que dans les 7 derniers jours par rapport à maintenant
            ddg_generator = ddgs.text(
                optimized_query, 
                region=current_region, 
                max_results=max_results, 
                backend="lite",
                timelimit="w"
            )
            if ddg_generator:
                for r in ddg_generator:
                    results.append({
                        "title": r.get("title", ""),
                        "content": r.get("body", r.get("snippet", "Pas de description disponible.")),
                        "url": r.get("href", "")
                    })
        
        # PLAN B : Sécurité si aucun résultat trouvé avec le filtre (on garde le timelimit="w")
        if not results and target_sites:
            print(f"🔄 [WebSearch DDG] Aucun résultat cette semaine sur les sites experts. Repli mondial...")
            with DDGS() as ddgs:
                ddg_generator = ddgs.text(
                    f"football {optimized_query}", 
                    region="fr-fr", 
                    max_results=max_results, 
                    backend="lite",
                    timelimit="w"
                )
                if ddg_generator:
                    for r in ddg_generator:
                        results.append({
                            "title": r.get("title", ""),
                            "content": r.get("body", "Pas de description disponible."),
                            "url": r.get("href", "")
                        })

        print(f"✅ [WebSearch DDG] {len(results)} résultats de la semaine récupérés.")
        return {
            "results": results,
            "images": []
        }
        
    except Exception as e:
        print(f"❌ Erreur lors de la recherche DuckDuckGo (Filtre Hebdomadaire) : {e}")
        return {"results": [], "images": []}