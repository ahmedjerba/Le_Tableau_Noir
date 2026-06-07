# Le Tableau Noir ⚽

> Génération automatique de magazines sportifs par architecture multi-agents LLM.

---

## Présentation

**Le Tableau Noir** est une application de génération de magazines sportifs pilotée par une architecture multi-agents orchestrée avec LangGraph. À partir d'un simple sujet (ex : *"Le Real Madrid en Juin 2026"*), le système recherche, agrège et rédige automatiquement un magazine complet au format Markdown avec un ton journalistique.

---

## Architecture

```
Sujet
  │
  ▼
PlannerNode  (llama-3.3-70b-versatile)
  │  Initialise le plan de rédaction
  │
  ▼
┌─────────────────────────────────────────────┐
│  7 Agents en parallèle (llama-3.1-8b-instant) │
│                                              │
│  GeneralAgent   → Scores & résultats         │
│  StatsAgent     → xG & métriques avancées    │
│  MercatoAgent   → Transferts & rumeurs       │
│  TactiqueAgent  → Formations & analyse       │
│  BlessuresAgent → Infirmerie & retours       │
│  ContexteAgent  → Classement & saison        │
│  MediaAgent     → Déclarations & presse      │
└─────────────────────────────────────────────┘
  │  Chaque agent retourne un JSON structuré
  │
  ▼
EnricherNode        ← (recommandé)
  │  Normalisation dates · déduplication · scoring fraîcheur
  │
  ▼
ValidatorAgent
  │  Contrôle qualité JSON · scoring confiance · routing conditionnel
  │    ├─ OK           → WriterAgent
  │    ├─ retry        → Agents (max 2 tentatives)
  │    └─ dégradé      → WriterAgent en mode partiel
  │
  ▼
WriterAgent  (llama-3.3-70b-versatile)
  │  Agrégation des JSON · rédaction Markdown journalistique
  │
  ▼
HallucinationGuard  ← (recommandé)
  │  Cross-check entités · détection claims non supportés
  │
  ▼
Magazine Markdown
```

---

## Stack technique

| Composant | Technologie |
|---|---|
| Orchestration | LangGraph (graphe cyclique/parallèle) |
| LLM planification & rédaction | `llama-3.3-70b-versatile` via Groq |
| LLM agents de recherche | `llama-3.1-8b-instant` via Groq |
| Recherche web | DuckDuckGo Search (`duckduckgo-search`) |
| Langage | Python 3.11+ |

---

## Installation

```bash
# Cloner le dépôt
git clone https://github.com/votre-user/le-tableau-noir.git
cd le-tableau-noir

# Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Windows : .venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

### Variables d'environnement

Créer un fichier `.env` à la racine :

```env
GROQ_API_KEY=votre_cle_groq
```

---

## Utilisation

```python
from graph import build_graph

graph = build_graph()

result = graph.invoke({
    "subject": "Le Real Madrid en Juin 2026",
    "max_retries": 2
})

print(result["final_article"])
```

---

## Structure du projet

```
le-tableau-noir/
├── agents/
│   ├── planner.py          # PlannerNode
│   ├── workers/
│   │   ├── general.py      # Scores & résultats
│   │   ├── stats.py        # xG & métriques
│   │   ├── mercato.py      # Transferts
│   │   ├── tactique.py     # Formations
│   │   ├── blessures.py    # Infirmerie
│   │   ├── contexte.py     # Classement
│   │   └── media.py        # Déclarations
│   ├── enricher.py         # EnricherNode
│   ├── validator.py        # ValidatorAgent
│   ├── writer.py           # WriterAgent
│   └── hallucination_guard.py
├── graph.py                # Définition du graphe LangGraph
├── state.py                # GraphState (TypedDict)
├── prompts/                # Prompts séparés par agent
├── utils/
│   ├── search.py           # Wrapper DuckDuckGo
│   └── json_utils.py       # Validation & parsing
├── requirements.txt
├── .env.example
└── README.md
```

---

## State

```python
class GraphState(TypedDict):
    subject: str
    plan: dict
    agent_results: dict[str, AgentResult]
    retry_count: dict[str, int]
    max_retries: int
    search_budget_exhausted: bool
    writer_attempts: int
    final_article: str | None
    hallucination_report: dict | None
```

---

## Contrat de données des agents

Chaque agent de recherche retourne ce JSON strict. `null` est obligatoire pour toute valeur manquante — les chaînes vides `""` sont interdites.

```json
{
  "agent": "general",
  "subject": "Le Real Madrid en Juin 2026",
  "retrieved_at": "2026-06-07T14:30:00Z",
  "data_freshness": "high | medium | low | unknown",
  "confidence": 0.85,
  "data": { },
  "sources": ["https://...", "https://..."],
  "search_returned_empty": false,
  "notes": null
}
```

---

## Gestion des données manquantes

Le `ValidatorAgent` route conditionnellement selon le nombre d'agents ayant retourné `search_returned_empty: true` :

| Agents vides | Mode Writer | Comportement |
|---|---|---|
| 0–1 | Normal | Rédaction complète |
| 2–3 | Averti | Sections manquantes signalées |
| 4+ | Dégradé | Encadré ⚠ en tête de magazine |

Le `WriterAgent` a l'interdiction absolue de combler un vide avec sa mémoire d'entraînement. Toute section sans données affiche : `**[Données indisponibles au {date}]**`

---

## Robustesse & anti-hallucination

- Requêtes DuckDuckGo contraintes temporellement (`timelimit="m"` — dernier mois)
- Détection du vide de recherche **avant** l'appel LLM pour ne pas consommer de tokens inutilement
- `EnricherNode` : calcul d'un `data_freshness_score` par agent
- `HallucinationGuard` : cross-check de chaque entité nommée (joueur, score, montant) contre les JSON sources avant publication
- Coupe-circuit `max_retries` pour éviter les boucles infinies

---

## Limitations connues

- DuckDuckGo peut retourner des résultats obsolètes sur des sujets très récents
- Le modèle 8b peut produire des JSON mal formés sur des recherches complexes — prévoir un fallback de parsing permissif
- Le parallélisme de 7 agents simultanés peut heurter les rate limits Groq — envisager 2 batches de 3-4

---

## Licence

MIT
