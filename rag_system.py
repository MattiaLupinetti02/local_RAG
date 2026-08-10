import os
import json
import faiss
import numpy as np
from documents_utils import make_file_set
from build_index import update_index_metadata
from ollama import Client

###########################################################
# Configurazione
###########################################################

INDEX_FOLDER = os.getenv("INDEX_FOLDER", "faiss")

TOP_k = int(os.getenv("TOP_K", 3))

INDEX_FILE = os.path.join(
    INDEX_FOLDER,
    os.getenv("INDEX_DOCUMENT", "index.faiss")
)

METADATA_FILE = os.path.join(
    INDEX_FOLDER,
    os.getenv("METADATA_DOCUMENT", "metadata.json")
)

DATA = os.getenv("DATA_FOLDER", "data")

SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.45))

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "bge-m3")

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


def reload_index_and_metadata():
    global index, metadata
    index = faiss.read_index(INDEX_FILE)
    with open(METADATA_FILE, encoding="utf-8") as f:
        metadata = json.load(f)



def update_index():
    

    file_set = set(os.listdir(DATA))
    indexed_file_set = make_file_set(metadata)
    new_files = file_set - indexed_file_set
    
    if new_files:
        print(f"Nuovi file trovati: {new_files}")
        update_index_metadata(file_set=new_files)
        reload_index_and_metadata()
        return True
    return False

        

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

def search_embedding_vectors(query,top_k=TOP_k):

    query_embedding = embed_query(query)

    scores, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    for score, idx in zip(scores[0], indices[0]):

        if idx == -1:
            continue

        """if score < SIMILARITY_THRESHOLD:
            continue"""

        results.append({

            "score": float(score),

            "file": metadata[idx]["file"],

            "text": metadata[idx].get("text", "")

        })

    return results