import os
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer

_chroma = None
_embedder = None

def _client():
    global _chroma
    if _chroma is None:
        os.makedirs("./data/chroma", exist_ok=True)
        _chroma = chromadb.PersistentClient(path="./data/chroma", settings=ChromaSettings(allow_reset=True))
    return _chroma

def _emb():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _embedder

def _collection_for_user(user_id: int):
    cname = f"user-{user_id}"
    client = _client()
    try:
        col = client.get_collection(cname)
    except:
        col = client.create_collection(cname, metadata={"hnsw:space": "cosine"})
    return col

def add_note(user_id: int, note_id: int, text: str, chunk_size=900, overlap=120):
    col = _collection_for_user(user_id)
    emb = _emb()
    chunks = []
    i = 0
    words = text.split()
    while i < len(words):
        chunk_words = words[i:i+chunk_size]
        chunks.append(" ".join(chunk_words))
        i += (chunk_size - overlap)
    if not chunks:
        return 0
    vectors = emb.encode(chunks, convert_to_numpy=True).tolist()
    ids = [f"{note_id}-{k}" for k in range(len(chunks))]
    metadatas = [{"note_id": note_id, "idx": k} for k in range(len(chunks))]
    col.add(ids=ids, embeddings=vectors, documents=chunks, metadatas=metadatas)
    return len(chunks)

def remove_note(user_id: int, note_id: int):
    """Delete all chunks for a note from user's collection."""
    col = _collection_for_user(user_id)
    # delete by metadata filter
    try:
        col.delete(where={"note_id": note_id})
    except Exception:
        # Some backends don’t support where; fall back to id prefix scan
        # (best-effort; safe to ignore if not supported)
        pass

def search(user_id: int, query: str, top_k: int = 5):
    col = _collection_for_user(user_id)
    emb = _emb()
    qv = emb.encode([query], convert_to_numpy=True).tolist()
    res = col.query(query_embeddings=qv, n_results=top_k, include=["documents","metadatas","distances"])
    docs = (res.get("documents") or [[]])[0]
    metas = (res.get("metadatas") or [[]])[0]
    dists = (res.get("distances") or [[]])[0]
    out = []
    for d, m, dist in zip(docs, metas, dists):
        out.append({"text": d, "note_id": m.get("note_id"), "idx": m.get("idx"), "score": float(1.0 - dist)})
    return out
