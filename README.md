# StudyBuddy — Tuteur IA Personnalisé

Système Multi-Agents (SMA) de tutorat intelligent basé sur RAG, construit avec Streamlit, ChromaDB et OpenRouter.  
Uploadez vos cours, chattez avec le tuteur IA, passez des quiz adaptatifs, et suivez vos lacunes.

> Projet IA Distribuée — EMSI Maroc

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
├── app.py                        ← Entrypoint Streamlit + router de pages
├── .env                          ← Clés API + chemins + config email
├── requirements.txt
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
├── frontend/
│   ├── design_system.py          ← Thème CSS + composants réutilisables
│   ├── i18n.py                   ← Internationalisation FR / EN
│   ├── page_login.py             ← Connexion / création de compte
│   ├── page_home.py              ← Tableau de bord : KPIs + progression
│   ├── page_courses.py           ← Upload, indexation, gestion des cours
│   ├── page_chat.py              ← Chat pédagogique avec rendu Markdown
│   ├── page_quiz.py              ← Quiz adaptatif QCM + HITL + email rapport
│   └── page_dashboard.py         ← Analytics : courbes, lacunes, plan d'étude IA
│
└── data/
    ├── courses/                  ← Fichiers uploadés + cours exemples (.txt)
    │   ├── machine_learning_fondamentaux.txt
    │   ├── deep_learning_reseaux_neurones.txt
    │   ├── nlp_et_grands_modeles_de_langage.txt
    │   └── big_data_hadoop_spark.txt
    ├── vectorstore/              ← Index ChromaDB persistant (auto-créé)
    └── studybuddy.db             ← Base SQLite (auto-créée)
```

---

## Démarrage rapide

```bash
# 1. Environnement virtuel
python -m venv venv
source venv/bin/activate          # Windows : venv\Scripts\activate
pip install -r requirements.txt

# 2. Configurer .env
OPENROUTER_API_KEY=sk-or-...      # https://openrouter.ai/keys
OPENROUTER_MODEL=mistralai/mistral-7b-instruct
FALLBACK_MODEL=google/gemma-2-9b-it:free
FILIERE=IA & Data Science

# 3. Lancer
streamlit run app.py
```

Ouvrir **http://localhost:8501**

> Au premier lancement, les 4 cours exemples (ML, Deep Learning, NLP, Big Data) sont automatiquement indexés dans ChromaDB. Le RAG fonctionne immédiatement sans upload manuel.

---

## Fonctionnement Détaillé

### Couche 1 — Orchestration (AgentOrchestrator)

L'orchestrateur centralise tous les appels IA et gère la résilience :

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
- Réponses en 4 modes : défaut, pas-à-pas, exemple concret, résumé
- Gestion automatique de la fenêtre de contexte :
  - Si > 10 messages → résumé automatique des anciens échanges via LLM
  - Conserve les 4 derniers messages intacts

**Agent 2 — AssessmentAgent** (`assessment_agent.py`)
- Génère des QCM basés strictement sur le contenu du cours (RAG)
- **Self-Correction Loop** : si le JSON généré est invalide, demande au LLM de se corriger (max 3 tentatives avec feedback d'erreur précis)
- Utilise le modèle de fallback à la 3ème tentative
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
- Chaque appel est logué (timestamp, outil, succès/échec)
- Interprétation du retour d'action → chemin de repli si erreur

**Gmail SMTP** (`email_service.py`)
- Rapport de quiz HTML (score, verdict, concepts à revoir)
- Résumé hebdomadaire de progression
- Déclenché depuis la page quiz ou le dashboard

**Human-in-the-Loop (HITL)**
- Confirmation obligatoire avant soumission du quiz
- L'étudiant voit le nombre de réponses données et valide manuellement
- Évite les soumissions accidentelles qui impactent le profil d'apprentissage

**Boucle d'observation & Fallback**
- Retry exponentiel sur chaque appel LLM (2s → 4s → 8s)
- Basculement automatique vers `FALLBACK_MODEL` si le modèle principal échoue
- Messages d'erreur gracieux affichés à l'utilisateur en cas d'indisponibilité

---

## Configuration Gmail (optionnel)

Pour activer les rapports email, ajoutez dans `.env` :

```env
GMAIL_USER=votre@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
```

Créez un mot de passe d'application sur :  
**myaccount.google.com → Sécurité → Mots de passe des applications**

---

## Modèles LLM supportés

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
| `openai` | Client OpenRouter (compatible OpenAI) |
| `streamlit` | Interface web |
| `chromadb` | Base vectorielle locale persistante |
| `sentence-transformers` | Embeddings multilingues |
| `pdfplumber` | Extraction texte PDF |
| `python-docx` | Extraction texte DOCX |
| `plotly` | Graphiques de progression |

---

## Notes

- Le modèle d'embeddings (~120 MB) se télécharge au premier lancement puis est mis en cache.
- Le singleton d'embeddings est thread-safe (double-checked locking) pour éviter le rechargement entre les reruns Streamlit.
- La base SQLite utilise le mode WAL pour les accès concurrents.
- Les cours exemples sont auto-indexés uniquement si la base est vide.
