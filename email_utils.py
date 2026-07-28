from rag_system import search

import json
import os

DATA_FOLDER = "data"


def read_email(filename):

    with open(
        os.path.join(DATA_FOLDER, filename),
        encoding="utf-8"
    ) as f:

        return json.load(f)


def cerca_mail(query):

    results = search(query)

    emails = []

    for result in results:

        email = read_email(result["file"])

        emails.append({

            "score": result["score"],

            "email": email

        })

    return emails