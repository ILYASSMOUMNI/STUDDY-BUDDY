#!/usr/bin/env python3
# scripts/test_setup.py
# Vérifie que tout est bien installé et configuré (version Gemini)

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

print("=" * 55)
print("  StudyBuddy — Vérification installation (Gemini)")
print("=" * 55)

errors = []

# ── 1. Variables d'environnement ──
print("\n[1/5] Variables d'environnement...")
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY") or os.getenv("OPENROUTER_API_KEY", "")
model   = os.getenv("GEMINI_MODEL") or os.getenv("OPENROUTER_MODEL", "gemini-2.0-flash")

if not api_key or len(api_key) < 20:
    errors.append("GEMINI_API_KEY non configurée dans .env")
    print("  ❌ GEMINI_API_KEY manquante")
else:
    provider = "Gemini" if api_key.startswith("AIzaSy") else "OpenRouter"
    print(f"  ✅ Clé API {provider} configurée (...{api_key[-8:]})")

print(f"  ✅ Modèle : {model}")

# ── 2. Bibliothèques ──
print("\n[2/5] Bibliothèques Python...")
libs = [
    ("openai",                "openai"),
    ("fastapi",               "fastapi"),
    ("chromadb",              "chromadb"),
    ("sentence_transformers", "sentence-transformers"),
    ("pdfplumber",            "pdfplumber"),
    ("docx",                  "python-docx"),
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

# ── 5. API Gemini ──
print("\n[5/5] Connexion à l'API Gemini...")
if any("GEMINI_API_KEY" in e for e in errors):
    print("  ⏭️  Ignoré (clé API manquante)")
else:
    try:
        from openai import OpenAI

        if api_key.startswith("AIzaSy"):
            base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
            headers = {}
        else:
            base_url = "https://openrouter.ai/api/v1"
            headers = {"HTTP-Referer": "https://studybuddy.emsi.ma", "X-Title": "StudyBuddy EMSI"}

        client = OpenAI(api_key=api_key, base_url=base_url, default_headers=headers)
        response = client.chat.completions.create(
            model=model,
            max_tokens=30,
            messages=[{"role": "user", "content": "Réponds juste 'OK StudyBuddy' en français."}]
        )
        reply = response.choices[0].message.content.strip()
        print(f"  ✅ API OK — Modèle : {model}")
        print(f"     Réponse test : {reply}")
    except Exception as e:
        errors.append(f"Gemini API : {e}")
        print(f"  ❌ Erreur : {e}")
        print("     → Vérifie ta clé sur https://aistudio.google.com/app/apikey")
        print("     → Vérifie que le modèle est bien : gemini-2.0-flash")

# ── Résumé ──
print("\n" + "=" * 55)
if errors:
    print(f"  ❌ {len(errors)} erreur(s) à corriger :")
    for e in errors:
        print(f"     → {e}")
    print()
    print("  Corrige ces erreurs avant de lancer server.py")
else:
    print("  ✅ Tout est OK ! Lance l'application :")
    print()
    print("     uvicorn server:app --reload --port 8000")
    print()
    print("  Puis ouvre : http://localhost:8000")
print("=" * 55)
