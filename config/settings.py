from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
FOOTBALL_API_KEY = (os.getenv("FOOTBALL_API_KEY") or os.getenv("Football_API_KEY") or "").strip()


def ensure_groq_api_key() -> str:
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "Configuration manquante: définis GROQ_API_KEY dans le fichier .env à la racine du projet."
        )
    return api_key

# LLM settings placeholder
LLM_SETTINGS = {
    "provider": "groq",
    "model": "llama-3.3-70b-versatile",
}
