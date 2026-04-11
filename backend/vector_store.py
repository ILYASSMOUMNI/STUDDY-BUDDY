# backend/vector_store.py
# Gestion de la base vectorielle ChromaDB + embeddings sentence-transformers

import os
import json
from typing import List, Dict, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

VECTORSTORE_DIR = os.getenv("VECTORSTORE_DIR", "./data/vectorstore")
EMBED_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Singleton pattern pour ne charger le modèle qu'une fois
_embed_model = None
_chroma_client = None


def get_embed_model() -> SentenceTransformer:
    global _embed_model
    if _embed_model is None:
        print("[VECTOR] Chargement du modèle d'embeddings...")
        _embed_model = SentenceTransformer(EMBED_MODEL_NAME)
        print("[VECTOR] Modèle chargé ✅")
    return _embed_model


def get_chroma_client() -> chromadb.PersistentClient:
    global _chroma_client
    if _chroma_client is None:
        Path(VECTORSTORE_DIR).mkdir(parents=True, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(
            path=VECTORSTORE_DIR,
            settings=Settings(anonymized_telemetry=False)
        )
    return _chroma_client


def _collection_name(course_id: int) -> str:
    return f"course_{course_id}"


def index_course(course_id: int, chunks: List[Dict]) -> int:
    """
    Indexe les chunks d'un cours dans ChromaDB.
    chunks: [{"chunk_id": int, "text": str, ...}]
    Retourne le nombre de chunks indexés.
    """
    client = get_chroma_client()
    model = get_embed_model()
    col_name = _collection_name(course_id)

    # Supprimer la collection si elle existe déjà (re-indexation)
    try:
        client.delete_collection(col_name)
    except Exception:
        pass

    collection = client.create_collection(
        name=col_name,
        metadata={"hnsw:space": "cosine"}
    )

    texts = [c["text"] for c in chunks]
    ids = [f"{course_id}_{c['chunk_id']}" for c in chunks]
    metadatas = [{"course_id": course_id, "chunk_id": c["chunk_id"]} for c in chunks]

    # Encoder par batch
    batch_size = 32
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        embeddings = model.encode(batch, show_progress_bar=False).tolist()
        all_embeddings.extend(embeddings)

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=all_embeddings,
        metadatas=metadatas
    )

    print(f"[VECTOR] Cours {course_id} indexé : {len(chunks)} chunks")
    return len(chunks)


def search(course_id: int, query: str, top_k: int = 5) -> List[Dict]:
    """
    Recherche sémantique dans les chunks d'un cours.
    Retourne les top_k chunks les plus pertinents.
    """
    client = get_chroma_client()
    model = get_embed_model()
    col_name = _collection_name(course_id)

    try:
        collection = client.get_collection(col_name)
    except Exception:
        return []

    query_embedding = model.encode([query], show_progress_bar=False).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(top_k, collection.count()),
        include=["documents", "distances", "metadatas"]
    )

    if not results["documents"] or not results["documents"][0]:
        return []

    chunks = []
    for i, doc in enumerate(results["documents"][0]):
        chunks.append({
            "text": doc,
            "distance": results["distances"][0][i],
            "chunk_id": results["metadatas"][0][i].get("chunk_id")
        })

    return chunks


def search_all_courses(query: str, top_k: int = 3) -> List[Dict]:
    """
    Recherche dans tous les cours indexés (mode généraliste).
    """
    client = get_chroma_client()
    model = get_embed_model()

    all_results = []
    collections = client.list_collections()

    query_embedding = model.encode([query], show_progress_bar=False).tolist()

    for col_info in collections:
        try:
            col = client.get_collection(col_info.name)
            results = col.query(
                query_embeddings=query_embedding,
                n_results=min(top_k, col.count()),
                include=["documents", "distances", "metadatas"]
            )
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    all_results.append({
                        "text": doc,
                        "distance": results["distances"][0][i],
                        "collection": col_info.name
                    })
        except Exception:
            continue

    # Trier par distance (plus petit = plus similaire)
    all_results.sort(key=lambda x: x["distance"])
    return all_results[:top_k * 2]


def delete_course_index(course_id: int):
    """Supprime l'index d'un cours."""
    client = get_chroma_client()
    try:
        client.delete_collection(_collection_name(course_id))
        print(f"[VECTOR] Index du cours {course_id} supprimé")
    except Exception as e:
        print(f"[VECTOR] Impossible de supprimer l'index {course_id}: {e}")


def course_is_indexed(course_id: int) -> bool:
    """Vérifie si un cours est déjà indexé."""
    client = get_chroma_client()
    try:
        col = client.get_collection(_collection_name(course_id))
        return col.count() > 0
    except Exception:
        return False
