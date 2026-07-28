import os
import json
import faiss
import numpy as np

from ollama import Client

###############################################################
# Configurazione
###############################################################

DATA_FOLDER = "data"
INDEX_FOLDER = "faiss"

INDEX_FILE = os.path.join(INDEX_FOLDER, "emails.index")
METADATA_FILE = os.path.join(INDEX_FOLDER, "metadata.json")

EMBEDDING_MODEL = "bge-m3"

client = Client(
    host=os.getenv(
        "OLLAMA_HOST",
        "http://localhost:11434"
    )
)


###############################################################
# Recupera tutte le email
###############################################################

documents = []
metadata = []

files = sorted(
    [
        f for f in os.listdir(DATA_FOLDER)
        if f.endswith(".json")
    ]
)

print(f"Trovate {len(files)} email.")

for filename in files:

    path = os.path.join(DATA_FOLDER, filename)

    with open(path, encoding="utf-8") as f:

        email = json.load(f)

    text = f"""
Oggetto:
{email['subject']}

Mittente:
{email['from']}

Data:
{email['date']}

Corpo:
{email['body']}
"""

    documents.append(text)

    metadata.append({
        "file": filename
    })


###############################################################
# Embedding
###############################################################

print("Calcolo embedding...")

response = client.embed(
    model=EMBEDDING_MODEL,
    input=documents
)

embeddings = np.array(
    response["embeddings"],
    dtype=np.float32
)

###############################################################
# Normalizzazione
###############################################################

faiss.normalize_L2(embeddings)

###############################################################
# Costruzione indice
###############################################################

dimension = embeddings.shape[1]

index = faiss.IndexFlatIP(dimension)

index.add(embeddings)

###############################################################
# Salvataggio
###############################################################

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