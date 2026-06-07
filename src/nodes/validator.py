# src/nodes/validator_agent.py

from typing import Dict, Any, List
from src.state import DigestState

class ValidatorAgentNode:
    def __init__(self):
        pass

    def __call__(self, state: DigestState) -> Dict[str, Any]:
        print("\n[ValidatorAgent] 🔍 Analyse des rapports JSON des 7 agents de recherche...")
        
        retry_list = []

        # 1. Validation : info_general (GeneralAgent)
        info_gen = state.get("info_general", [])
        if not info_gen:
            retry_list.append("general_agent")
        else:
            dernier_gen = info_gen[-1] if isinstance(info_gen[-1], dict) else {}
            if not dernier_gen.get("actualites_majeures") or "stabilisation" in str(dernier_gen):
                print("⚠️ [Validator] L'actualité générale est vide ou non pertinente.")
                retry_list.append("general_agent")

        # 2. Validation : info_mercato (MercatoAgent)
        info_mer = state.get("info_mercato", [])
        if not info_mer:
            retry_list.append("mercato_agent")
        else:
            dernier_mer = info_mer[-1] if isinstance(info_mer[-1], dict) else {}
            if "Calme plat" in str(dernier_mer.get("rumeurs_chaudes", "")):
                print("⚠️ [Validator] Les données du Mercato Agent ont basculé sur le fallback.")
                retry_list.append("mercato_agent")

        # 3. Validation : info_histoire (HistoireAgent)
        info_hist = state.get("info_histoire", [])
        if not info_hist:
            retry_list.append("histoire_agent")
        else:
            dernier_hist = info_hist[-1] if isinstance(info_hist[-1], dict) else {}
            if "regorge d'anecdotes épiques" in str(dernier_hist.get("recit", "")):
                print("⚠️ [Validator] L'anecdote historique n'a pas pu être extraite via Wikipedia.")
                retry_list.append("histoire_agent")

        # 4. Validation : info_stats (StatsAgent)
        info_stats = state.get("info_stats", [])
        if not info_stats:
            print("⚠️ [Validator] Aucune donnée statistique avancée n'a été collectée.")
            retry_list.append("stats_agent")
        else:
            dernier_stat = info_stats[-1] if isinstance(info_stats[-1], dict) else {}
            focus = dernier_stat.get("focus_data_equipe", {})
            if "indisponible" in str(focus.get("metrique_cle_club", "")).lower():
                print("⚠️ [Validator] Les statistiques avancées contiennent des anomalies ou le fallback.")
                retry_list.append("stats_agent")

        # 5. Validation : info_scoop_sur_equipe (ScoopTeamAgent)
        info_scoop_eq = state.get("info_scoop_sur_equipe", [])
        if not info_scoop_eq:
            retry_list.append("scoop_team_agent")
        else:
            dernier_eq = info_scoop_eq[-1] if isinstance(info_scoop_eq[-1], dict) else {}
            if "Calme plat en coulisses" in str(dernier_eq.get("scoop_vestiaire", "")):
                print("⚠️ [Validator] L'agent scoop équipe n'a trouvé aucune info exclusive.")
                retry_list.append("scoop_team_agent")

        # 6. Validation : info_scoop_sur_joueur (ScoopPlayerAgent)
        info_scoop_jo = state.get("info_scoop_sur_joueur", [])
        if not info_scoop_jo:
            retry_list.append("scoop_player_agent")
        else:
            dernier_jo = info_scoop_jo[-1] if isinstance(info_scoop_jo[-1], dict) else {}
            if "Focus terrain uniquement" in str(dernier_jo.get("buzz_declaration", "")):
                print("⚠️ [Validator] L'agent scoop joueur n'a trouvé aucun buzz croustillant.")
                retry_list.append("scoop_player_agent")

        # 7. Validation : info_funny (FunnyAgent)
        info_fun = state.get("info_funny", [])
        if not info_fun:
            retry_list.append("funny_agent")
        else:
            dernier_fun = info_fun[-1] if isinstance(info_fun[-1], dict) else {}
            troll = dernier_fun.get("le_troll_du_club", {})
            if "Calme plat" in str(troll.get("sujet", "")):
                print("⚠️ [Validator] L'info rigolote globale est restée sur le fallback.")
                retry_list.append("funny_agent")

        # --- ARBITRAGE DU GRAPH ---
        if retry_list:
            print(f"❌ [Validator] Validation ÉCHOUÉE. Demande de correction envoyée au routeur pour : {retry_list}\n")
            return {
                "validation_status": "RETRY",
                "retry_agents": retry_list
            }
        
        print("✅ [Validator] Validation RÉUSSIE. Toutes les pièces du puzzle sont conformes et structurées !\n")
        return {
            "validation_status": "APPROVED",
            "retry_agents": []
        }