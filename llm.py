import os

from ollama import Client


MODEL = "llama3.2"

client = Client(
    host=os.getenv(
        "OLLAMA_HOST",
        "http://localhost:11434"
    )
)


SYSTEM_PROMPT = """
Sei un assistente specializzato nella ricerca di email.

Riceverai:

- una domanda dell'utente

- alcune email recuperate tramite RAG

Devi rispondere solamente utilizzando
le informazioni presenti nelle email.

Se il contesto non contiene la risposta,
dillo chiaramente.

Non inventare informazioni.

Quando possibile cita:

- oggetto della mail

- mittente

- data
"""


def ask_llm(question: str, context: str):

    prompt = f"""
        EMAIL RECUPERATE

        {context}

        --------------------------------------------

        DOMANDA

        {question}

        --------------------------------------------

        RISPOSTA
        """

    response = client.chat(

        model=MODEL,

        messages=[

            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },

            {
                "role": "user",
                "content": prompt
            }

        ]

    )

    return response["message"]["content"]