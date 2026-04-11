# 📚 StudyBuddy — IA Tuteur pour IA & Data Science

> Projet IA Distribuée — EMSI Morocco  
> Tuteur IA basé sur RAG (Retrieval-Augmented Generation) + Claude (Anthropic)

---

## 🏗️ Architecture

```
studybuddy/
├── app.py                    ← Point d'entrée Streamlit + routeur
├── .env                      ← Configuration (API Key, chemins)
├── requirements.txt          ← Dépendances Python
├── .streamlit/
│   └── config.toml           ← Config Streamlit (port, thème)
│
├── backend/
│   ├── database.py           ← SQLite : étudiants, cours, quiz, lacunes
│   ├── course_parser.py      ← Extraction texte PDF/DOCX + chunking
│   ├── vector_store.py       ← ChromaDB + embeddings sentence-transformers
│   └── ai_tutor.py           ← Moteur IA : Claude API + RAG + quiz
│
├── frontend/
│   ├── page_login.py         ← Connexion / inscription
│   ├── page_home.py          ← Accueil avec stats
│   ├── page_courses.py       ← Upload et gestion des cours
│   ├── page_chat.py          ← Chat avec le tuteur IA
│   ├── page_quiz.py          ← Quiz adaptatif + détection lacunes
│   └── page_dashboard.py     ← Analytics et progression
│
├── data/
│   ├── courses/              ← Fichiers PDF/DOCX uploadés
│   ├── vectorstore/          ← Base ChromaDB (auto-créée)
│   └── studybuddy.db         ← Base SQLite (auto-créée)
│
└── scripts/
    ├── deploy_azure.sh       ← Script déploiement Azure Linux VM
    └── start_windows.bat     ← Auto-start Azure Windows VM
```

---

## 🚀 Installation rapide

### Étape 1 — Cloner et configurer

```bash
# Cloner le projet
git clone <ton-repo> studybuddy
cd studybuddy

# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate          # Linux/Mac
# venv\Scripts\activate.bat       # Windows

# Installer les dépendances
pip install -r requirements.txt
```

### Étape 2 — Configurer la clé API

Édite le fichier `.env` :

```env
ANTHROPIC_API_KEY=sk-ant-TON_VRAI_CLE_ICI
CLAUDE_MODEL=claude-3-5-sonnet-20241022
FILIERE=IA & Data Science
```

> 💡 Récupère ta clé sur : https://console.anthropic.com/

### Étape 3 — Lancer

```bash
streamlit run app.py
```

Ouvre ton navigateur sur : **http://localhost:8501**

---

## ☁️ Déploiement Azure VM

### Option A — VM Linux (Ubuntu)

```bash
# 1. Se connecter à la VM
ssh ton-user@IP-VM-AZURE

# 2. Uploader le projet
scp -r studybuddy/ ton-user@IP-VM-AZURE:~/

# 3. Lancer le script de déploiement
cd ~/studybuddy
bash scripts/deploy_azure.sh

# 4. Lancer en production (arrière-plan)
source venv/bin/activate
mkdir -p logs
nohup streamlit run app.py --server.port 8501 --server.address 0.0.0.0 > logs/app.log 2>&1 &
echo $! > studybuddy.pid
```

### Option B — VM Windows (ta config actuelle)

```bat
REM 1. Copier le projet dans C:\StudyBuddy
REM 2. Ouvrir PowerShell en administrateur :

cd C:\StudyBuddy
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

REM 3. Configurer .env avec ta clé API

REM 4. Lancer :
streamlit run app.py --server.port 8501 --server.address 0.0.0.0

REM 5. Pour l'auto-start : copier start_windows.bat dans le dossier Startup Windows
```

### Ouvrir le port 8501 sur Azure

```
Azure Portal → Ta VM → Networking → Inbound port rules
→ Add inbound port rule :
   - Destination port: 8501
   - Protocol: TCP
   - Action: Allow
   - Priority: 1001
   - Name: StudyBuddy
```

Accès : **http://[IP-PUBLIQUE-AZURE]:8501**

---

## 🔧 Comment ça marche

### Pipeline RAG

```
PDF/DOCX uploadé
    ↓
course_parser.py → extraction texte → nettoyage → chunks (800 mots, overlap 150)
    ↓
vector_store.py → embeddings (sentence-transformers multilingue) → ChromaDB
    ↓
Question étudiant → recherche sémantique → top 5 chunks pertinents
    ↓
Claude API → réponse contextualisée au cours
```

### Détection des lacunes

```
Quiz QCM généré par Claude (basé sur les chunks du cours)
    ↓
Réponses de l'étudiant → comparaison → mauvaises réponses enregistrées
    ↓
analyze_weaknesses() → Claude identifie les concepts mal compris
    ↓
weaknesses table (SQLite) → fail_count incrémenté par concept
    ↓
generate_targeted_quiz() → quiz ciblé sur les concepts faibles
```

---

## 📦 Dépendances principales

| Bibliothèque | Rôle |
|---|---|
| `anthropic` | API Claude pour le tuteur IA |
| `streamlit` | Interface web |
| `chromadb` | Base vectorielle locale |
| `sentence-transformers` | Embeddings multilingues |
| `pdfplumber` | Extraction texte PDF |
| `python-docx` | Extraction texte DOCX |
| `plotly` | Graphiques dashboard |
| `sqlite3` | Base de données (intégré Python) |

---

## 🐛 Dépannage

### Erreur : `ANTHROPIC_API_KEY not found`
→ Vérifie que le fichier `.env` existe et contient ta vraie clé API

### Erreur : `chromadb` crash
→ `pip install chromadb --upgrade`

### Le modèle d'embeddings est lent au 1er démarrage
→ Normal ! Il télécharge ~120MB. Ensuite il est en cache.

### Port 8501 inaccessible depuis l'extérieur
→ Vérifie les règles NSG Azure ET le firewall de la VM

---

## 👨‍💻 Développé pour

**Projet IA Distribuée — EMSI Morocco**  
Filière : IA & Data Science  
