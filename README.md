# StudyBuddy — Tuteur IA Personnalisé

Système Multi-Agents (SMA) de tutorat intelligent basé sur RAG.
Uploadez vos cours, chattez avec le tuteur IA, passez des quiz adaptatifs et suivez vos lacunes.

> Projet IA Distribuée — EMSI Maroc

---

## Versions disponibles

| Version | Interface | Commande de lancement | Port |
|---------|-----------|----------------------|------|
| **v2** (recommandée) | FastAPI + SPA (Alpine.js + Tailwind) | `python server.py` | 8000 |
| v1 (legacy) | Streamlit | `streamlit run app.py` | 8501 |

Les deux versions partagent exactement le même backend (`backend/`), la même base SQLite et le même index ChromaDB.

---

## Architecture Globale du Système (4 Couches)

```
┌─────────────────────────────────────────────────────────────────┐
│  COUCHE 1 — Orchestration                                       │
│  AgentOrchestrator : routing, retry exponentiel, fallback model │
├─────────────────────────────────────────────────────────────────┤
│  COUCHE 2 — Cognitive (3 Agents distincts)                      │
│  TutorAgent · AssessmentAgent · AnalysisAgent                   │
├─────────────────────────────────────────────────────────────────┤
│  COUCHE 3 — Connaissance                                        │
│  ChromaDB (Vector DB) + SentenceTransformers embeddings         │
├─────────────────────────────────────────────────────────────────┤
│  COUCHE 4 — Action & Résilience                                 │
│  MCP Server · Gmail SMTP · Self-Correction Loop · HITL          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Structure du Projet

```
studybuddy/
├── server.py                     ← Entrypoint v2 — FastAPI REST API (14 routes)
├── app.py                        ← Entrypoint v1 — Streamlit (legacy)
├── .env                          ← Clés API + chemins + config email
├── requirements.txt
│
├── static/                       ← Frontend v2 (SPA, aucun build requis)
│   ├── index.html                ← Shell HTML + CDN (Tailwind, Alpine.js, marked.js)
│   └── app.js                    ← Logique Alpine.js : login, dashboard, chat, quiz...
│
├── backend/
│   ├── agents/                   ← Système Multi-Agents (Couche 2)
│   │   ├── tutor_agent.py        ← Agent 1 : Tuteur pédagogique (RAG + mémoire)
│   │   ├── assessment_agent.py   ← Agent 2 : Évaluateur (quiz + auto-correction JSON)
│   │   ├── analysis_agent.py     ← Agent 3 : Analyste (lacunes + plan d'étude)
│   │   └── orchestrator.py       ← Orchestrateur : routing, retry, fallback
│   │
│   ├── mcp_server.py             ← Serveur MCP : abstraction SQL/vectorstore/fichiers
│   ├── email_service.py          ← Service Gmail SMTP (rapports HTML)
│   ├── sample_courses.py         ← Auto-indexation des cours exemples au démarrage
│   │
│   ├── database.py               ← SQLite : étudiants, cours, quiz, lacunes
│   ├── course_parser.py          ← Extraction PDF/DOCX/TXT + chunking (800 mots, overlap 150)
│   ├── vector_store.py           ← ChromaDB + embeddings multilingues (thread-safe)
│   └── ai_tutor.py               ← Façade publique → délègue à l'orchestrateur
│
├── frontend/                     ← Pages Streamlit v1 (legacy)
│   ├── design_system.py
│   ├── i18n.py
│   ├── page_login.py
│   ├── page_home.py
│   ├── page_courses.py
│   ├── page_chat.py
│   ├── page_quiz.py
│   └── page_dashboard.py
│
└── data/
    ├── courses/                  ← Fichiers uploadés
    ├── vectorstore/              ← Index ChromaDB persistant (auto-créé)
    └── studybuddy.db             ← Base SQLite (auto-créée)
```

---

## Démarrage rapide

### Prérequis

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### Configurer `.env`

```env
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=mistralai/mistral-7b-instruct
FALLBACK_MODEL=google/gemma-2-9b-it:free
FILIERE=IA & Data Science

# Optionnel — rapports email
GMAIL_USER=votre@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
```

Obtenez votre clé API sur [openrouter.ai/keys](https://openrouter.ai/keys).

### Lancer v2 (recommandé)

```bash
python server.py
# ou
uvicorn server:app --reload --port 8000
```

Ouvrir **http://localhost:8000**

### Lancer v1 (Streamlit)

```bash
streamlit run app.py
```

Ouvrir **http://localhost:8501**

> Au premier lancement, les cours exemples sont automatiquement indexés dans ChromaDB. Le RAG fonctionne immédiatement sans upload manuel.

---

## Fonctionnalités v2 (FastAPI + SPA)

| Vue | Description |
|-----|-------------|
| **Login** | Connexion/création de compte, session persistante (localStorage) |
| **Tableau de bord** | KPIs, progression par cours, activité récente, recommandations personnalisées |
| **Tuteur IA** | Chat avec markdown, 5 modes de réponse, sélection du cours ou base complète |
| **Quiz** | Génération IA, QCM interactif, feedback instantané, analyse des lacunes |
| **Bibliothèque** | Upload PDF/DOCX/TXT par glisser-déposer, indexation vectorielle automatique |
| **Progression** | Statistiques détaillées, score par cours, concepts à retravailler |

---

## Fonctionnement Détaillé

### Couche 1 — Orchestration (AgentOrchestrator)

```
Requête utilisateur
  → Sélection de l'agent (Tutor / Assessment / Analysis)
  → Construction du contexte RAG (ChromaDB via MCP)
  → Appel LLM avec retry exponentiel (×3, délai 2s/4s/8s)
  → En cas d'échec : fallback vers FALLBACK_MODEL
  → Retour de la réponse ou message d'erreur gracieux
```

### Couche 2 — Agents Cognitifs

**Agent 1 — TutorAgent** (`tutor_agent.py`)

- System prompt pédagogique spécialisé (EMSI, filière IA & Data Science)
- Réponses en 5 modes : défaut, explication, pas-à-pas, exemple concret, résumé
- Gestion automatique de la fenêtre de contexte (résumé auto si > 10 messages)

**Agent 2 — AssessmentAgent** (`assessment_agent.py`)

- Génère des QCM basés strictement sur le contenu du cours (RAG)
- **Self-Correction Loop** : si le JSON est invalide, demande au LLM de se corriger (max 3 tentatives)
- Évalue aussi les réponses ouvertes avec feedback constructif

**Agent 3 — AnalysisAgent** (`analysis_agent.py`)

- Identifie les lacunes conceptuelles à partir des erreurs de quiz
- Génère un plan d'étude personnalisé (sessions avec durée, activité, priorité)
- Produit un rapport de progression textuel (FR/EN)

### Couche 3 — Base de Connaissances (RAG)

```
PDF / DOCX / TXT uploadé
  → course_parser.py    extraction texte + nettoyage
  → split_into_chunks() découpage 800 mots, overlap 150 mots
  → SentenceTransformers embeddings multilingues (paraphrase-multilingual-MiniLM-L12-v2)
  → ChromaDB            indexation avec métrique cosinus (HNSW)

Requête étudiant
  → embedding de la query
  → recherche sémantique top-5 (distance cosinus < 0.85)
  → contexte RAG injecté dans le prompt LLM
  → réponse ancrée sur le cours
```

### Couche 4 — Action & Résilience

**MCP Server** (`mcp_server.py`)
- Implémentation du Model Context Protocol (abstraction unifiée)
- 6 outils enregistrés : `get_student_profile`, `search_knowledge`, `save_quiz_result`, `list_courses`, `get_course_progress`, `read_local_file`

**Gmail SMTP** (`email_service.py`)
- Rapport de quiz HTML (score, verdict, concepts à revoir)
- Résumé hebdomadaire de progression

**Human-in-the-Loop (HITL)**
- Confirmation obligatoire avant soumission du quiz

**Boucle d'observation & Fallback**
- Retry exponentiel sur chaque appel LLM (2s → 4s → 8s)
- Basculement automatique vers `FALLBACK_MODEL` si le modèle principal échoue

---

## API REST (v2)

| Méthode | Route | Description |
|---------|-------|-------------|
| POST | `/api/auth/login` | Connexion / création de compte |
| GET | `/api/courses` | Liste des cours indexés |
| POST | `/api/courses` | Upload + indexation d'un cours |
| DELETE | `/api/courses/{id}` | Suppression cours + index |
| POST | `/api/chat` | Message au tuteur IA |
| GET | `/api/chat/history/{student_id}` | Historique de conversation |
| POST | `/api/quiz/generate` | Génération de quiz QCM |
| POST | `/api/quiz/submit` | Soumission + analyse des résultats |
| GET | `/api/dashboard/{student_id}` | Données tableau de bord |
| GET | `/api/progress/{student_id}` | Progression détaillée |

Documentation interactive : **http://localhost:8000/api/docs**

---

## Modèles LLM supportés (via OpenRouter)

| Modèle | Type | Usage recommandé |
|--------|------|-----------------|
| `mistralai/mistral-7b-instruct` | Gratuit | Modèle principal (défaut) |
| `google/gemma-2-9b-it:free` | Gratuit | Fallback |
| `openai/gpt-4o-mini` | Payant | Meilleure qualité |
| `anthropic/claude-3-haiku` | Payant | Réponses rapides et précises |

---

## Dépendances principales

| Bibliothèque | Rôle |
|---|---|
| `fastapi` + `uvicorn` | Serveur API v2 |
| `openai` | Client OpenRouter (compatible OpenAI) |
| `streamlit` | Interface web v1 (legacy) |
| `chromadb` | Base vectorielle locale persistante |
| `sentence-transformers` | Embeddings multilingues |
| `pdfplumber` | Extraction texte PDF |
| `python-docx` | Extraction texte DOCX |

---

## Notes techniques

- Le modèle d'embeddings (~120 MB) se télécharge au premier lancement puis est mis en cache.
- Le singleton d'embeddings est thread-safe (double-checked locking).
- La base SQLite utilise le mode WAL pour les accès concurrents.
- La v2 ne nécessite aucun build frontend — tout est servi depuis `static/` via CDN.
