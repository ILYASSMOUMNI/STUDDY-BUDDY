#!/usr/bin/env python3
# scripts/test_setup.py
# Vérifie que tout est bien installé et configuré (version OpenRouter)

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

print("=" * 55)
print("  StudyBuddy — Vérification installation (OpenRouter)")
print("=" * 55)

errors = []

# ── 1. Variables d'environnement ──
print("\n[1/5] Variables d'environnement...")
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY", "")
model   = os.getenv("OPENROUTER_MODEL", "mistralai/mistral-7b-instruct")

if not api_key or "VOTRE_CLE" in api_key or len(api_key) < 20:
    errors.append("OPENROUTER_API_KEY non configurée dans .env")
    print("  ❌ OPENROUTER_API_KEY manquante")
else:
    print(f"  ✅ OPENROUTER_API_KEY configurée (...{api_key[-8:]})")

print(f"  ✅ Modèle : {model}")

# ── 2. Bibliothèques ──
print("\n[2/5] Bibliothèques Python...")
libs = [
    ("openai",                "openai"),
    ("streamlit",             "streamlit"),
    ("chromadb",              "chromadb"),
    ("sentence_transformers", "sentence-transformers"),
    ("pdfplumber",            "pdfplumber"),
    ("docx",                  "python-docx"),
    ("plotly",                "plotly"),
    ("pandas",                "pandas"),
]
for module, name in libs:
    try:
        __import__(module)
        print(f"  ✅ {name}")
    except ImportError:
        errors.append(f"{name} non installé")
        print(f"  ❌ {name}  →  pip install {name}")

# ── 3. Base de données ──
print("\n[3/5] Base de données SQLite...")
try:
    from backend.database import init_db, get_all_courses
    init_db()
    courses = get_all_courses()
    print(f"  ✅ SQLite OK — {len(courses)} cours enregistré(s)")
except Exception as e:
    errors.append(f"SQLite : {e}")
    print(f"  ❌ {e}")

# ── 4. Modèle d'embeddings ──
print("\n[4/5] Modèle d'embeddings multilingue...")
try:
    from sentence_transformers import SentenceTransformer
    m = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    emb = m.encode(["test studybuddy"])
    print(f"  ✅ Modèle chargé — dimension vecteur : {emb.shape[1]}")
except Exception as e:
    errors.append(f"Embeddings : {e}")
    print(f"  ❌ {e}")

# ── 5. API OpenRouter ──
print("\n[5/5] Connexion à l'API OpenRouter...")
if any("OPENROUTER_API_KEY" in e for e in errors):
    print("  ⏭️  Ignoré (clé API manquante)")
else:
    try:
        from openai import OpenAI
        client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://studybuddy.emsi.ma",
                "X-Title": "StudyBuddy EMSI"
            }
        )
        response = client.chat.completions.create(
            model=model,
            max_tokens=30,
            messages=[{"role": "user", "content": "Réponds juste 'OK StudyBuddy' en français."}]
        )
        reply = response.choices[0].message.content.strip()
        print(f"  ✅ OpenRouter OK — Modèle : {model}")
        print(f"     Réponse test : {reply}")
    except Exception as e:
        errors.append(f"OpenRouter API : {e}")
        print(f"  ❌ Erreur : {e}")
        print("     → Vérifie ta clé sur https://openrouter.ai/keys")
        print("     → Vérifie que le modèle existe : https://openrouter.ai/models")

# ── Résumé ──
print("\n" + "=" * 55)
if errors:
    print(f"  ❌ {len(errors)} erreur(s) à corriger :")
    for e in errors:
        print(f"     → {e}")
    print()
    print("  Corrige ces erreurs avant de lancer app.py")
else:
    print("  ✅ Tout est OK ! Lance l'application :")
    print()
    print("     streamlit run app.py")
    print()
    print("  Puis ouvre : http://localhost:8501")
    print()
    print("  Sur Azure VM :")
    print("     streamlit run app.py --server.address 0.0.0.0 --server.port 8501")
print("=" * 55)
