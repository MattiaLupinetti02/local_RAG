import os
import json
import faiss
import numpy as np

from loader.email_loader import load_emails
from loader.document_loader import load_pdfs
from loader.markdown_loader import load_markdown_files


from ollama import Client

# Configurazione

DATA_FOLDER = os.getenv("DATA_FOLDER")
INDEX_FOLDER = os.getenv("INDEX_FOLDER")

INDEX_FILE = os.path.join(INDEX_FOLDER, os.getenv("INDEX_DOCUMENT"))
METADATA_FILE = os.path.join(INDEX_FOLDER, os.getenv("METADATA_DOCUMENT"))

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
client = Client(
    host=os.getenv(
        "OLLAMA_HOST",
        "http://localhost:11434"
    )
)




def build_index_and_metadata(file_set=None):

    documents = []
    documents += load_emails(DATA_FOLDER, file_set=file_set)
    documents += load_pdfs(DATA_FOLDER, file_set=file_set)
    documents += load_markdown_files(DATA_FOLDER, file_set=file_set)
    texts = [d["text"] for d in documents]

    if not documents:
        return np.array([]), []

    metadata = []
    for d in documents:
        entry = dict(d["metadata"])
        entry["text"] = d["text"]
        metadata.append(entry)


    print("Calcolo embedding...")

    response = client.embed(
        model=EMBEDDING_MODEL,
        input=texts
                            )

    embeddings = np.array(
        response["embeddings"],
        dtype=np.float32
    )
    return embeddings, metadata


def update_index_metadata(file_set=None):
    new_embeddings, new_metadata = build_index_and_metadata(file_set=file_set)
    if len(new_metadata) == 0:
        print("Nessun nuovo documento da indicizzare.")
        return

    # 2. Normalizzazione L2 obbligatoria prima di FAISS
    faiss.normalize_L2(new_embeddings)
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            old_metadata = json.load(f)
    else:
        old_metadata = []

    # Unisci i metadati
    full_metadata = old_metadata + new_metadata
    # 4. Carica l'indice FAISS dal file, aggiungi vettori e salva su disco
    if os.path.exists(INDEX_FILE):
        index = faiss.read_index(INDEX_FILE)
    else:
        dimension = new_embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)

    index.add(new_embeddings)
    os.makedirs(INDEX_FOLDER, exist_ok=True)
    faiss.write_index(index, INDEX_FILE)
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(
            full_metadata,
            f,
            ensure_ascii=False,
            indent=4
        )

if __name__ == "__main__":
    embeddings, metadata = build_index_and_metadata()
    if len(embeddings) > 0:
        faiss.normalize_L2(embeddings)
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)
        index.add(embeddings)

        os.makedirs(INDEX_FOLDER, exist_ok=True)
        faiss.write_index(index, INDEX_FILE)
        with open(METADATA_FILE, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)
        print("Indice FAISS creato da zero.")