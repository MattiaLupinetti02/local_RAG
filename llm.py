import os

from ollama import Client


MODEL = os.getenv("MODEL", "llama3.2")

client = Client(
    host=os.getenv(
        "OLLAMA_HOST",
        "http://localhost:11434"
    )
)


SYSTEM_PROMPT = """
Sei un assistente specializzato nella ricerca di email, file markdown e, pdf.

Riceverai:

- una domanda dell'utente

- alcune email, file markdown e, pdf recuperate tramite RAG

Devi rispondere solamente utilizzando
le informazioni presenti in email, file markdown e, pdf. Tu non puoi inventare informazioni o fare supposizioni. ma devi eseguire 
sintesi, analisi richieste, comparazioni, estrazioni di informazioni e, ragionamenti logici.

Se il contesto non contiene la risposta,
dillo chiaramente.

Non inventare informazioni.

Quando possibile cita:

- oggetto della mail

- mittente

- body della mail

- file markdown

- file pdf
"""


def ask_llm(question: str, context: str):

    prompt = f"""
        DOCUMENTI RECUPERATI

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