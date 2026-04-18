"""
Auto-indexation des cours exemples au démarrage.
Si la base de données est vide, indexe automatiquement les cours .txt du dossier data/courses/.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv

load_dotenv()

COURSES_DIR = Path(os.getenv("COURSES_DIR", "./data/courses"))
FILIERE     = os.getenv("FILIERE", "IA & Data Science")

_SAMPLE_FILES = [
    "machine_learning_fondamentaux.txt",
    "deep_learning_reseaux_neurones.txt",
    "nlp_et_grands_modeles_de_langage.txt",
    "big_data_hadoop_spark.txt",
]


def init_sample_courses() -> List[str]:
    """
    Vérifie si des cours existent en base.
    Si la base est vide, parse et indexe les cours exemples automatiquement.
    Retourne la liste des titres indexés.
    """
    from backend.database import get_all_courses, save_course
    from backend.vector_store import index_course, course_is_indexed

    existing = get_all_courses()
    indexed_titles: List[str] = []

    if existing:
        return []  # Des cours existent déjà — rien à faire

    print("[SampleCourses] Base vide — chargement des cours exemples...")

    for filename in _SAMPLE_FILES:
        path = COURSES_DIR / filename
        if not path.exists():
            print(f"[SampleCourses] Fichier introuvable : {path}")
            continue

        try:
            # Dériver un titre lisible depuis le nom de fichier
            title = (
                filename.replace("_", " ")
                        .replace(".txt", "")
                        .title()
            )

            # Parser et chunker
            raw_text = path.read_text(encoding="utf-8")
            from backend.course_parser import clean_text, split_into_chunks
            chunks = split_into_chunks(clean_text(raw_text), chunk_size=800, overlap=150)

            if not chunks:
                print(f"[SampleCourses] Aucun chunk extrait pour {filename}")
                continue

            # Sauvegarder en base
            course_id = save_course(
                title=title,
                filename=filename,
                filiere=FILIERE,
                num_chunks=len(chunks),
            )

            # Indexer dans ChromaDB
            if not course_is_indexed(course_id):
                index_course(course_id, chunks)

            print(f"[SampleCourses] ✅ '{title}' — {len(chunks)} chunks indexés (ID={course_id})")
            indexed_titles.append(title)

        except Exception as e:
            print(f"[SampleCourses] ❌ Erreur pour {filename} : {e}")

    return indexed_titles
