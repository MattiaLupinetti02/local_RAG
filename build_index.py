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

documents = []
documents += load_emails(DATA_FOLDER)
documents += load_pdfs(DATA_FOLDER)
documents += load_markdown_files(DATA_FOLDER)
texts = [d["text"] for d in documents]
metadata = [d["metadata"] for d in documents]





print("Calcolo embedding...")

response = client.embed(
    model=EMBEDDING_MODEL,
    input=texts
                        )

embeddings = np.array(
    response["embeddings"],
    dtype=np.float32
)

# Normalizzazione

faiss.normalize_L2(embeddings)

# Costruzione indice

dimension = embeddings.shape[1]

index = faiss.IndexFlatIP(dimension)

index.add(embeddings)

# Salvataggio

os.makedirs(INDEX_FOLDER, exist_ok=True)

faiss.write_index(index, INDEX_FILE)

with open(METADATA_FILE, "w", encoding="utf-8") as f:
    json.dump(
        metadata,
        f,
        ensure_ascii=False,
        indent=4
    )

print("Indice FAISS creato.")
