import os
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

INDEX_DIR = "index"

model = SentenceTransformer("BAAI/bge-small-en")

db_cache = {}


def load_db(db_name):
    if db_name in db_cache:
        return db_cache[db_name]

    path = os.path.join(INDEX_DIR, db_name)

    index = faiss.read_index(f"{path}/faiss.index")

    with open(f"{path}/meta.pkl", "rb") as f:
        documents, metadatas = pickle.load(f)

    with open(f"{path}/bm25.pkl", "rb") as f:
        bm25 = pickle.load(f)

    db_cache[db_name] = (index, documents, metadatas, bm25)
    return db_cache[db_name]


def hybrid_search(query, db_name, top_k=5):
    index, documents, metadatas, bm25 = load_db(db_name)

    q_vec = model.encode([query]).astype("float32")
    D, I = index.search(q_vec, top_k * 3)

    vector_hits = I[0]

    tokenized_query = query.split()
    bm25_scores = bm25.get_scores(tokenized_query)
    bm25_hits = np.argsort(bm25_scores)[::-1][:top_k * 3]

    candidates = list(set(vector_hits) | set(bm25_hits))

    scored = []
    for i in candidates:
        scored.append((i, bm25_scores[i]))

    scored = sorted(scored, key=lambda x: x[1], reverse=True)

    results = []
    for i, _ in scored[:top_k]:
        results.append({
            "text": documents[i],
            "meta": metadatas[i]
        })

    return results