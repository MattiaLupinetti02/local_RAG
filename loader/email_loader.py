
import os
import json

import os
import json
from nylas import Client
from loader.types.chunk import Chunk
import json
from nylas import Client
from bs4 import BeautifulSoup

def esporta_email_nylas(data_folder="data", limite=100, sort_by = "date", order="desc") :
    api_key = os.environ.get("NYLAS_API_KEY")
    grant_id = os.environ.get("NYLAS_GRANT_ID")
    if not api_key or not grant_id:
        raise ValueError("NYLAS_API_KEY e NYLAS_GRANT_ID devono essere impostate")

    nylas = Client(api_key=api_key)
    os.makedirs(data_folder, exist_ok=True)

    params = {"limit": limite}

    esportati = 0
    page_token = None

    print("Starting exporting emails")

    while True:
        query_params = dict(params)
        if page_token:
            query_params["page_token"] = page_token

        response = nylas.messages.list(
            identifier=grant_id,
            query_params=query_params,
        )

        messages = response.data
        request_id = response.request_id
        next_cursor = response.next_cursor  # None se non c'è una pagina successiva

        for msg_summary in messages:
            if limite is not None and esportati >= limite:
                print(f"Limit {limite} reached, stopping export.")
                return esportati

            # la list restituisce solo lo snippet, serve una find() per il body completo
            msg, _, _ = nylas.messages.find(
                identifier=grant_id, message_id=msg_summary.id
            )

            body_html = getattr(msg, "body", "") or ""
            if body_html:
                try:
                    soup = BeautifulSoup(body_html, "html.parser")
                    body_clean = soup.get_text(separator=" ", strip=True)
                except Exception as e:
                    print(f"Errore parsing HTML email {esportati}: {e}")
                    body_clean = body_html
            else:
                body_clean = ""
            """print("=" * 40)
            print(msg)
            print("=" * 40)
            print(str(getattr(msg, "from_", None)))
            for f in getattr(msg, "from_", []):
                for k,v in f.items():
                    print(k,v)"""

            email_dict = {
                "id": msg.id,
                "subject": getattr(msg, "subject", ""),
                "from": getattr(msg, "from_", None)  ,
                # ... to/cc/bcc con lo stesso pattern che avevi già
                "date": str(getattr(msg, "date", "")),
                "body": body_clean,
                "snippet": getattr(msg, "snippet", ""),
                "thread_id": getattr(msg, "thread_id", ""),
                "attachments": [
                    {
                        "id": getattr(a, "id", ""),
                        "name": getattr(a, "filename", ""),
                        "size": getattr(a, "size", 0),
                        "content_type": getattr(a, "content_type", ""),
                    }
                    for a in (getattr(msg, "attachments", None) or [])
                ],
            }
            """print("="*100)
            print(email_dict)"""
            filename = os.path.join(data_folder, f"email_{esportati}.json")
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(email_dict, f, indent=2, default=str)

            esportati += 1
            if esportati % 100 == 0:
                print(f"📊 Esportate {esportati} email...")

        if not next_cursor:
            break
        page_token = next_cursor

    print(f"✅ Esportazione completata! {esportati} email salvate in {data_folder}")
    return esportati




def load_emails(data_folder, file_set=None) -> list[Chunk]:
    """
    Carica tutte le email in formato JSON dalla cartella specificata.
    Ogni email viene convertita in un dizionario con testo e metadati.
    """

    esporta_email_nylas(data_folder = data_folder)
    documents: list[Chunk]= []
    metadata = []

    files = sorted(
            [
                f for f in os.listdir(data_folder)
                if f.endswith(".json")
            ]
        )


    if file_set is not None:
        files = [f for f in files if f in file_set]
    

    print(f"Trovate {len(files)} email.")

    for filename in files:

        path = os.path.join(data_folder, filename)

        with open(path, encoding="utf-8") as f:

            email = json.load(f)



        documents.append({"file": filename,
                            "type": "email",
                            "text": f"{email['body']} \n subject: {email['subject']} \n sender: {email['from']} \n date: {email['date']}"
                            })


    print(f"Recuperate {len(documents)} email.")
    return documents
