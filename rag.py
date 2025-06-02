import faiss
import numpy as np
from preprocess import embedder

chunks = []  # you should keep scope from where you call build_index

def build_index(chunks_list):
    global chunks
    chunks = chunks_list
    embs = np.vstack(embedder.encode(chunks))
    idx = faiss.IndexFlatL2(embs.shape[1])
    idx.add(embs)
    return idx, embs

def retrieve(idx, embs, query: str, k=3):
    q_emb = embedder.encode([query])
    D, I = idx.search(q_emb, k)
    return [chunks[i] for i in I[0]]