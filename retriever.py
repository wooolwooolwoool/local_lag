import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

INDEX_DIR = "index"

model = SentenceTransformer("BAAI/bge-small-en")

# load
index = faiss.read_index(f"{INDEX_DIR}/faiss.index")

with open(f"{INDEX_DIR}/meta.pkl", "rb") as f:
    documents, metadatas = pickle.load(f)

with open(f"{INDEX_DIR}/bm25.pkl", "rb") as f:
    bm25 = pickle.load(f)


def hybrid_search(query, top_k=5):
    # embedding search
    q_vec = model.encode([query]).astype("float32")
    D, I = index.search(q_vec, top_k * 3)

    vector_hits = I[0]

    # bm25 search
    tokenized_query = query.split()
    bm25_scores = bm25.get_scores(tokenized_query)
    bm25_hits = np.argsort(bm25_scores)[::-1][:top_k * 3]

    # merge
    candidates = list(set(vector_hits) | set(bm25_hits))

    # simple rerank (by vector distance)
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