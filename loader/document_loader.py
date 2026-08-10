# loaders/pdf_loader.py
import os
from unstructured.partition.pdf import partition_pdf
from unstructured.chunking.title import chunk_by_title

def load_pdfs(folder,file_set = None, max_characters=1000, overlap=150, strategy="fast"):
    """
    strategy:
      - "fast": solo estrazione testuale, no layout detection (leggero, veloce)
      - "hi_res": layout detection con modello ML (tabelle, titoli precisi, più lento)
      - "ocr_only": per PDF scansionati (immagini, no testo estraibile)
    """
    documents = []


    files = sorted(
                [
                    f for f in os.listdir(folder)
                    if f.endswith(".pdf")
                ]
            )


    if file_set is not None:
        files = [f for f in files if f in file_set]
        


    for filename in files:


        path = os.path.join(folder, filename)

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