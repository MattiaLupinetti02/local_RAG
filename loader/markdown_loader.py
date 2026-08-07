
import os
import json
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_markdown_files(data_folder):
    """
    Carica tutti i file in formato Markdown dalla cartella specificata.
    Ogni file viene convertito in un dizionario con testo e metadati.
    """


    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    documents = []
    metadata = []

    files = sorted(
        [
            f for f in os.listdir(data_folder)
            if f.endswith(".md")
        ]
    )

    print(f"Trovati {len(files)} file Markdown.")

    for filename in files:

        path = os.path.join(data_folder, filename)

        with open(path, encoding="utf-8") as f:

            text = f.read()

        chunks = splitter.split_text(text)

        for i, chunk in enumerate(chunks):
            documents.append({
                "text": chunk,
                "metadata": {
                    "file": filename,
                    "type": "markdown",
                    "chunk_index": i
                }
            })
    print(f"Recuperati {len(documents)} file Markdown.")
    return documents
