from time import time
from typing import Any, Dict
import random
import time


from langchain_groq import ChatGroq

from config.settings import ensure_groq_api_key


def _normalize_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.split()).strip()


def compact_query_target(value: Any, max_words: int = 2) -> str:
    text = _normalize_text(value)
    if not text:
        return ""
    return " ".join(text.split()[:max_words])


def resolve_primary_team(state: Dict[str, Any]) -> str:
    for key in ("club_phare", "target_team", "team_target"):
        candidate = _normalize_text(state.get(key))
        if candidate:
            return candidate

    planned_sections = state.get("planned_sections", []) or []
    for section in planned_sections:
        candidate = _normalize_text(section.get("target"))
        if candidate and candidate.lower() not in {"global", "monde", "world"}:
            return candidate

    preferences = state.get("user_preferences", {}) or {}
    teams = preferences.get("teams", []) or []
    if teams:
        candidate = _normalize_text(teams[0])
        if candidate:
            return candidate

    return ""


def resolve_primary_player(state: Dict[str, Any]) -> str:
    for key in ("joueur_star", "target_player", "player_target"):
        candidate = _normalize_text(state.get(key))
        if candidate:
            return candidate

    planned_sections = state.get("planned_sections", []) or []
    for section in planned_sections:
        if section.get("agent_type") == "scoop_player_agent":
            candidate = _normalize_text(section.get("target"))
            if candidate:
                return candidate

    preferences = state.get("user_preferences", {}) or {}
    players = preferences.get("players", []) or []
    if players:
        candidate = _normalize_text(players[0])
        if candidate:
            return candidate

    return ""


def build_football_query(*parts: Any, max_words: int = 4) -> str:
    tokens = ["football"]
    for part in parts:
        candidate = _normalize_text(part)
        if candidate:
            tokens.extend(candidate.split())

    return " ".join(tokens[:max_words])


def create_groq_llm(temperature: float, model: str = "llama-3.1-8b-instant") -> ChatGroq:
    ensure_groq_api_key()
    delai_securite = random.uniform(0.5, 2.5)
    
    print(f"[Groq Factory] Micro-pause de sécurité de {delai_securite:.2f}s pour le modèle {model}...")
    time.sleep(delai_securite)
    
    # 3. Instanciation et retour du modèle
    return ChatGroq(model=model, temperature=temperature)
