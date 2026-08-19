import os
import json
import faiss
import numpy as np

from loader.email_loader import load_emails
from loader.document_loader import load_pdfs
from loader.markdown_loader import load_markdown_files

from ollama import Client


# ============================================================
# Configurazione
# ============================================================

DATA_FOLDER = os.getenv("DATA_FOLDER")
INDEX_FOLDER = os.getenv("INDEX_FOLDER")

INDEX_FILE = os.path.join(
    INDEX_FOLDER,
    os.getenv("INDEX_DOCUMENT")
)

METADATA_FILE = os.path.join(
    INDEX_FOLDER,
    os.getenv("METADATA_DOCUMENT")
)

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "32"))

client = Client(
    host=os.getenv(
        "OLLAMA_HOST",
        "http://localhost:11434"
    )
)


# ============================================================
# Costruzione embedding
# ============================================================

def build_index_and_metadata(file_set=None):

    documents = []

    documents += load_emails(
        DATA_FOLDER,
        file_set=file_set
    )

    documents += load_pdfs(
        DATA_FOLDER,
        file_set=file_set
    )

    documents += load_markdown_files(
        DATA_FOLDER,
        file_set=file_set
    )

    if not documents:
        return np.array([], dtype=np.float32), []

    print(f"Documenti/chunk da indicizzare: {len(documents)}")
    print(f"Batch size: {BATCH_SIZE}")
    print(f"Modello embedding: {EMBEDDING_MODEL}")

    texts = [
        json.dumps(
            document,
            ensure_ascii=False
        )
        for document in documents
    ]

    all_embeddings = []

    total = len(texts)

    for start in range(0, total, BATCH_SIZE):

        end = min(
            start + BATCH_SIZE,
            total
        )

        batch_texts = texts[start:end]

        print(
            f"Calcolo embedding "
            f"{start + 1}-{end}/{total}..."
        )

        try:

            response = client.embed(
                model=EMBEDDING_MODEL,
                input=batch_texts
            )

            batch_embeddings = np.asarray(
                response["embeddings"],
                dtype=np.float32
            )

            all_embeddings.append(
                batch_embeddings
            )

        except Exception as e:

            print(
                f"ERRORE nel batch "
                f"{start + 1}-{end}: {e}"
            )

            raise

    embeddings = np.vstack(
        all_embeddings
    )

    print(
        f"Embedding completati: "
        f"{embeddings.shape}"
    )

    return embeddings, documents


def update_index_metadata(file_set=None):

    new_embeddings, new_metadata = (build_index_and_metadata(file_set=file_set))

    if len(new_metadata) == 0:
        print(
            "Nessun nuovo documento da indicizzare."
        )
        return

    faiss.normalize_L2(new_embeddings)


    if os.path.exists(METADATA_FILE):

        with open(
            METADATA_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            old_metadata = json.load(f)

    else:

        old_metadata = []

    full_metadata = (
        old_metadata +
        new_metadata
    )

    # --------------------------------------------------------
    # Indice FAISS
    # --------------------------------------------------------

    if os.path.exists(INDEX_FILE):

        index = faiss.read_index(
            INDEX_FILE
        )

    else:

        dimension = new_embeddings.shape[1]

        index = faiss.IndexFlatIP(
            dimension
        )

    index.add(
        new_embeddings
    )

    # --------------------------------------------------------
    # Salvataggio
    # --------------------------------------------------------

    os.makedirs(
        INDEX_FOLDER,
        exist_ok=True
    )

    faiss.write_index(
        index,
        INDEX_FILE
    )

    with open(
        METADATA_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            full_metadata,
            f,
            ensure_ascii=False,
            indent=4
        )

    print(
        f"Indice aggiornato. "
        f"Totale vettori: {index.ntotal}"
    )


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    embeddings, metadata = (
        build_index_and_metadata()
    )

    if len(embeddings) > 0:

        faiss.normalize_L2(
            embeddings
        )

        dimension = embeddings.shape[1]

        index = faiss.IndexFlatIP(
            dimension
        )

        index.add(
            embeddings
        )

        os.makedirs(
            INDEX_FOLDER,
            exist_ok=True
        )

        faiss.write_index(
            index,
            INDEX_FILE
        )

        with open(
            METADATA_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                metadata,
                f,
                ensure_ascii=False,
                indent=4
            )

        print(
            f"Indice FAISS creato da zero. "
            f"Vettori: {index.ntotal}"
        )