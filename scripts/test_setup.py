#!/usr/bin/env python3
# scripts/test_setup.py
# Vérifie que tout est bien installé et configuré

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

print("=" * 50)
print("  StudyBuddy — Vérification de l'installation")
print("=" * 50)

errors = []
warnings = []

# ── 1. Variables d'environnement ──
print("\n[1/5] Variables d'environnement...")
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY", "")
if not api_key or "VOTRE_CLE" in api_key:
    errors.append("OPENAI_API_KEY non configurée dans .env")
else:
    print(f"  ✅ OPENAI_API_KEY configurée (sk-...{api_key[-6:]})")

model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
print(f"  ✅ Modèle : {model}")

# ── 2. Imports bibliothèques ──
print("\n[2/5] Bibliothèques Python...")
libs = [
    ("openai", "openai"),
    ("streamlit", "streamlit"),
    ("chromadb", "chromadb"),
    ("sentence_transformers", "sentence-transformers"),
    ("pdfplumber", "pdfplumber"),
    ("docx", "python-docx"),
    ("plotly", "plotly"),
    ("pandas", "pandas"),
]

for module, name in libs:
    try:
        __import__(module)
        print(f"  ✅ {name}")
    except ImportError:
        errors.append(f"{name} non installé — pip install {name}")
        print(f"  ❌ {name}")

# ── 3. Base de données ──
print("\n[3/5] Base de données SQLite...")
try:
    from backend.database import init_db, get_all_courses
    init_db()
    courses = get_all_courses()
    print(f"  ✅ SQLite OK — {len(courses)} cours enregistrés")
except Exception as e:
    errors.append(f"Erreur SQLite : {e}")
    print(f"  ❌ {e}")

# ── 4. Modèle d'embeddings ──
print("\n[4/5] Modèle d'embeddings (peut prendre du temps)...")
try:
    from sentence_transformers import SentenceTransformer
    model_emb = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
    test_emb = model_emb.encode(["test"])
    print(f"  ✅ Modèle chargé — dimension : {test_emb.shape[1]}")
except Exception as e:
    errors.append(f"Modèle embeddings : {e}")
    print(f"  ❌ {e}")

# ── 5. API OpenAI ──
print("\n[5/5] Connexion à l'API OpenAI...")

openai_key = os.getenv("OPENAI_API_KEY", "")

if openai_key:
    try:
        from openai import OpenAI

        client = OpenAI(api_key=openai_key)

        response = client.responses.create(
            model=model,
            input="Dis juste 'OK StudyBuddy'"
        )

        # Extraction propre du texte
        output_text = ""
        for item in response.output:
            if hasattr(item, "content"):
                for content in item.content:
                    if hasattr(content, "text"):
                        output_text += content.text

        print(f"  ✅ API OK — Réponse : {output_text.strip()}")

    except Exception as e:
        errors.append(f"API OpenAI : {e}")
        print(f"  ❌ {e}")
else:
    errors.append("OPENAI_API_KEY non configurée")
    print("  ❌ Clé API OpenAI manquante")

# ── Résumé ──
print("\n" + "=" * 50)
if errors:
    print(f"  ❌ {len(errors)} erreur(s) détectée(s) :")
    for err in errors:
        print(f"     → {err}")
    print("\n  Corrige ces erreurs avant de lancer app.py")
else:
    print("  ✅ Tout est OK ! Lance l'application avec :")
    print()
    print("     streamlit run app.py")
    print()
    print("  Puis ouvre : http://localhost:8501")
print("=" * 50)