import os
import json
import faiss
import numpy as np

from ollama import Client

###########################################################
# Configurazione
###########################################################

INDEX_FOLDER = "faiss"

INDEX_FILE = os.path.join(
    INDEX_FOLDER,
    "emails.index"
)

METADATA_FILE = os.path.join(
    INDEX_FOLDER,
    "metadata.json"
)

SIMILARITY_THRESHOLD = 0.45

EMBEDDING_MODEL = "bge-m3"

client = Client(
    host=os.getenv(
        "OLLAMA_HOST",
        "http://localhost:11434"
    )
)

###########################################################
# Caricamento indice
###########################################################

index = faiss.read_index(INDEX_FILE)

with open(
    METADATA_FILE,
    encoding="utf-8"
) as f:

    metadata = json.load(f)


###########################################################
# Embedding query
###########################################################

def embed_query(query):

    response = client.embed(
        model=EMBEDDING_MODEL,
        input=[query]
    )

    embedding = np.array(
        response["embeddings"],
        dtype=np.float32
    )

    faiss.normalize_L2(embedding)

    return embedding


###########################################################
# Ricerca
###########################################################

def search(query,top_k=3):

    query_embedding = embed_query(query)

    scores, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    for score, idx in zip(scores[0], indices[0]):

        if idx == -1:
            continue

        if score < SIMILARITY_THRESHOLD:
            continue

        results.append({

            "score": float(score),

            "file": metadata[idx]["file"]

        })

    return results