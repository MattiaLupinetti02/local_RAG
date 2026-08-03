import os
import json
import faiss
import numpy as np

from loader.email_loader import load_emails
from loader.document_loader import load_pdfs


from ollama import Client

# Configurazione


DATA_FOLDER = "data"
INDEX_FOLDER = "faiss"

INDEX_FILE = os.path.join(INDEX_FOLDER, "documents.index")
METADATA_FILE = os.path.join(INDEX_FOLDER, "metadata.json")

EMBEDDING_MODEL = "bge-m3"
print(os.getenv("OLLAMA_HOST","http://localhost:11434"))
client = Client(
    host=os.getenv(
        "OLLAMA_HOST",
        "http://localhost:11434"
    )
)




documents = []
documents += load_emails(DATA_FOLDER)
documents += load_pdfs(DATA_FOLDER)

texts = [d["text"] for d in documents]
metadata = [d["metadata"] for d in documents]

print(documents)



# Embedding

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

print()

print("Indice FAISS creato.")

print(INDEX_FILE)

print(METADATA_FILE)