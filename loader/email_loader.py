
import os
import json

def load_emails(data_folder):
    """
    Carica tutte le email in formato JSON dalla cartella specificata.
    Ogni email viene convertita in un dizionario con testo e metadati.
    """
    documents = []
    metadata = []

    files = sorted(
        [
            f for f in os.listdir(data_folder)
            if f.endswith(".json")
        ]
    )

    print(f"Trovate {len(files)} email.")

    for filename in files:

        path = os.path.join(data_folder, filename)

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

        documents.append({
            "text": text,
            "metadata": {
                "file": filename
            }
        })


    print(f"Recuperate {len(documents)} email.")
    return documents
