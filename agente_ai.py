import streamlit as st

from email_utils import cerca_mail
from llm import ask_llm


##############################################################
# Configurazione pagina
##############################################################

st.set_page_config(
    page_title="Email Assistant",
    page_icon="📧",
    layout="wide"
)

##############################################################
# Stato della chat
##############################################################

if "messages" not in st.session_state:
    st.session_state.messages = []

##############################################################
# Titolo
##############################################################

st.title("📧 Email Assistant")

st.write(
    "Ricerca intelligente nelle email mediante RAG locale "
    "(FAISS + Ollama + Llama 3.2)"
)

##############################################################
# Visualizzazione cronologia
##############################################################

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

##############################################################
# Input utente
##############################################################

query = st.chat_input(
    "Scrivi una domanda..."
)

##############################################################
# Elaborazione
##############################################################

if query:

    ##########################################################
    # Messaggio utente
    ##########################################################

    st.session_state.messages.append(
        {
            "role": "user",
            "content": query
        }
    )

    with st.chat_message("user"):
        st.markdown(query)

    ##########################################################
    # Ricerca nel database vettoriale
    ##########################################################

    with st.spinner("Ricerca delle email..."):

        emails = cerca_mail(query)

    ##########################################################
    # Nessun risultato
    ##########################################################

    if len(emails) == 0:

        answer = (
            "Non ho trovato email sufficientemente "
            "attinenti alla richiesta."
        )

    else:

        ######################################################
        # Costruzione del contesto
        ######################################################

        context = ""

        for item in emails:

            score = item["score"]
            email = item["email"]

            context += f"""
                        ========================================

                        Similarità: {score:.3f}

                        Oggetto:
                        {email['subject']}

                        Mittente:
                        {email['from']}

                        Data:
                        {email['date']}

                        Corpo:
                        {email['body']}

                        ========================================

                    """

        ######################################################
        # Chiamata al modello
        ######################################################

        with st.spinner("Generazione risposta..."):

            answer = ask_llm(
                question=query,
                context=context
            )

    ##########################################################
    # Visualizzazione risposta
    ##########################################################

    with st.chat_message("assistant"):

        st.markdown(answer)

        with st.expander("Email recuperate dal RAG"):

            for item in emails:

                email = item["email"]

                st.markdown(
                    f"""
                        **Similarità:** {item['score']:.3f}

                        **Oggetto:** {email['subject']}

                        **Mittente:** {email['from']}

                        **Data:** {email['date']}

                        ---

                        {email['body']}

                        ---
                    """
                )

    ##########################################################
    # Salvataggio cronologia
    ##########################################################

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )