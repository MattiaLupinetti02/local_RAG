from rag_system import search_embedding_vectors

import json
import os
from unstructured.partition.pdf import partition_pdf
from unstructured.chunking.title import chunk_by_title


DATA_FOLDER = "data"


def read_email(filename):

    if filename.endswith(".json"):
        with open(
            os.path.join(DATA_FOLDER, filename),
            encoding="utf-8"
        ) as f:

            return json.load(f)



def read_pdfs(filename, max_characters=1000, overlap=150, strategy="fast"):
    """
    strategy:
      - "fast": solo estrazione testuale, no layout detection (leggero, veloce)
      - "hi_res": layout detection con modello ML (tabelle, titoli precisi, più lento)
      - "ocr_only": per PDF scansionati (immagini, no testo estraibile)
    """
    documents = []


    path = os.path.join(DATA_FOLDER, filename)

    elements = partition_pdf(
        filename=path,
        strategy=strategy,
    )

    chunks = chunk_by_title(
        elements,
        max_characters=max_characters,
        overlap=overlap,
    )

    for i, chunk in enumerate(chunks):
        documents.append({
            "text": str(chunk),
            "metadata": {
                "file": filename,
                "type": "pdf",
                "chunk_index": i,
                "page": getattr(chunk.metadata, "page_number", None),
            }
        })

    return documents

def search_documents(query):

    results = search_embedding_vectors(query)

    emails = []
    pdfs = []
    for result in results:
        print(result["file"])
        email = read_email(result["file"])

        emails.append({

            "score": result["score"],

            "email": email

        })
    for result in results:
        print(result["file"])
        pdf = read_pdfs(result["file"])
        for chunk in pdf:
            pdfs.append({

                "score": result["score"],

                "pdf": chunk["metadata"]["file"]+str(chunk["metadata"]["chunk_index"])

            })
    document_list = emails + pdfs
    print(document_list)
    print("Sorting documents by score...")
    return document_list