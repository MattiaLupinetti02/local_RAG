
import os
import json
from langchain_text_splitters import RecursiveCharacterTextSplitter
from loader.types.chunk import Chunk

def load_markdown_files(data_folder, file_set=None) -> list[Chunk]:
    """
    Carica tutti i file in formato Markdown dalla cartella specificata.
    Ogni file viene convertito in un dizionario con testo e metadati.
    """


    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    documents: list[Chunk] = []
    metadata = []

    files = sorted(
                [
                    f for f in os.listdir(data_folder)
                    if f.endswith(".md")
                ]
            )


    if file_set is not None:
        files = [f for f in files if f in file_set]

    print(f"Trovati {len(files)} file Markdown.")

    for filename in files:

        path = os.path.join(data_folder, filename)

        with open(path, encoding="utf-8") as f:

            text = f.read()

        chunks = splitter.split_text(text)

        for i, chunk in enumerate(chunks):
            print(f"Caricato chunk {i+1}/{len(chunks)} dal file {filename}.")
            documents.append({
                "text": chunk,
                "file": filename,
                "type": "markdown",
                "chunk_index": i
            })
    print(f"Recuperati {len(documents)} file Markdown.")
    return documents
