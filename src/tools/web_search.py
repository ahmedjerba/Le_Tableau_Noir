from duckduckgo_search import DDGS
from langchain_core.tools import tool
from typing import List, Union

@tool
def web_search(query: str, target_sites: Union[List[str], str] = None, max_results: int = 8) -> dict:
    """
    Effectue une recherche sur le web via DuckDuckGo pour obtenir les dernières infos du football.
    Prend en charge les sites français et internationaux (Marca, The Athletic, Sky Sports, etc.).
    """
    optimized_query = query
    is_international = False
    
    if target_sites:
        if isinstance(target_sites, str):
            sites_list = [s.strip().lower() for s in target_sites.split(",") if s.strip()]
        else:
            sites_list = [str(s).strip().lower() for s in target_sites if str(s).strip()]
            
        if sites_list:
            # Détection si on cherche sur des sites étrangers (.com, .es, etc.) pour adapter DuckDuckGo
            international_extensions = [".com", ".es", ".it", ".co.uk",".de",".co", ".net"]
            if any(any(ext in site for ext in international_extensions) for site in sites_list):
                is_international = True
                
            filter_parts = [f"site:{site}" for site in sites_list]
            site_filter = " (" + " OR ".join(filter_parts) + ")"
            optimized_query = f"{query}{site_filter}"
            print(f"🌐 [WebSearch DDG] Mode Multi-Sites ({'International' if is_international else 'Français'}) ➔ {len(sites_list)} sources ciblées pour : '{query}'")
    else:
        print(f"🌐 [WebSearch DDG] Mode Global ➔ Recherche générale pour : '{query}'")

    try:
        results = []
        # On adapte la région : vide (mondial) si international, sinon français
        current_region = "wt-wt" if is_international else "fr-fr"
        
        with DDGS() as ddgs:
            ddg_generator = ddgs.text(optimized_query, region=current_region, max_results=max_results, backend="lite")
            if ddg_generator:
                for r in ddg_generator:
                    results.append({
                        "title": r.get("title", ""),
                        "content": r.get("body", r.get("snippet", "Pas de description disponible.")),
                        "url": r.get("href", "")
                    })
        
        # PLAN B : Sécurité si aucun résultat trouvé
        if not results and target_sites:
            print(f"🔄 [WebSearch DDG] Aucun résultat sur les sites experts. Repli sur le Web Global...")
            with DDGS() as ddgs:
                ddg_generator = ddgs.text(f"football {query}", region="fr-fr", max_results=max_results, backend="lite")
                if ddg_generator:
                    for r in ddg_generator:
                        results.append({
                            "title": r.get("title", ""),
                            "content": r.get("body", "Pas de description disponible."),
                            "url": r.get("href", "")
                        })

        print(f"✅ [WebSearch DDG] {len(results)} résultats récupérés.")
        return {
            "results": results,
            "images": []
        }
        
    except Exception as e:
        print(f"❌ Erreur lors de la recherche DuckDuckGo : {e}")
        return {"results": [], "images": []}