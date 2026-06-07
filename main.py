# src/main.py

import os
from pathlib import Path
from dotenv import load_dotenv

# 🎯 CALCUL DU CHEMIN ABSOLU VERS LE DOSSIER DU SCRIPT
# __file__ est le chemin de main.py. .resolve().parent donne son dossier racine.
BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / ".env"

print(f"[Env Loader] Recherche du fichier .env ici : {env_path}")

# Chargement forcé via le chemin absolu
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print("✅ [Env Loader] Fichier .env trouvé et chargé avec succès.")
else:
    print("❌ [Env Loader] Erreur : Le fichier .env est introuvable à cet endroit ! Vérifie son emplacement.") 

if __name__ == "__main__":
    from config.settings import ensure_groq_api_key
    from src.graph import app

    ensure_groq_api_key()

    # Définition des préférences de ton abonné de test
    initial_state = {
        "user_preferences": {
            "teams": ["Real Madrid"],
            "players": ["Kylian Mbappé"],
            "leagues": ["La Liga", "Champions League"]
        },
        "time_window": "cette semaine",
        "sections_to_write": [],
        
        # 🚨 COMPTEUR DE RETRIES INITIALISÉ POUR LE VALIDATEUR ANTI-BOUCLE
        "retry_count": 0,
        
        # Initialisation obligatoire des canaux d'accumulation (operator.add)
        "info_general": [],
        "info_stats": [],
        "info_funny": [],
        "info_mercato": [],
        "info_scoop_sur_equipe": [],
        "info_scoop_sur_joueur": [],
        "info_histoire": [],
        
        # Planification initiale
        "planned_sections": [],
        "retry_agents": [],
        "validation_status": "PENDING"
    }

    print("🏁 Lancement de la génération du magazine 'Le Tableau Noir'...")
    print("🤖 Orchestration de l'équipe d'agents en parallèle (Groq + Llama 3.3)...")
    
    try:
        # Exécution du graphe LangGraph
        final_output = app.invoke(initial_state)
        
        markdown_result = final_output.get("final_markdown", "")
        status = final_output.get("status", "FAILED")

        if status == "SUCCESS" and markdown_result:
            print("\n--------------------------------------------------")
            print("✨ REVUE DE PRESSE GÉNÉRÉE AVEC SUCCÈS !")
            print("--------------------------------------------------\n")
            
            # Sauvegarde automatique du fichier Markdown dans un dossier dédié
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            file_path = os.path.join(output_dir, "tableau_noir_digest.md")
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(markdown_result)
                
            print(f"💾 Le magazine a été sauvegardé avec succès dans : {file_path}")
            print("💡 Conseil : Ouvre-le dans VS Code ou un aperçu Markdown pour apprécier la mise en page.\n")
            
            # Petit aperçu rapide dans ton terminal pour valider visuellement
            print("--- APERÇU DES PREMIÈRES LIGNES ---")
            print("\n".join(markdown_result.split("\n")[:15]))
            print("\n... (Le reste de la revue est disponible dans le fichier généré) ...")
        else:
            print("⚠️ Le WriterAgent a fini son exécution mais le livrable est vide ou en échec.")
            
    except Exception as e:
        print(f"\n❌ Erreur critique lors de l'exécution du pipeline LangGraph : {e}")