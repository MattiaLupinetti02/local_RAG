import streamlit as st

from email_utils import cerca_mail
from llm import ask_llm


##############################################################
# Configurazione pagina
##############################################################

st.set_page_config(
    page_title="Document Retrieval assistant",
    page_icon="�",
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

st.title("� Document Retrieval assistant")

st.write(
    "Smart retrieval of your documents"
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
    "Ask a question here"
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

    with st.spinner("Document research..."):

        emails = cerca_mail(query)

    ##########################################################
    # Nessun risultato
    ##########################################################

    if len(emails) == 0:

        answer = (
            "No relevant documents found for the request."
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

                        Similarity: {score:.3f}

                        Subject:
                        {email['subject']}

                        Sender:
                        {email['from']}

                        Date:
                        {email['date']}

                        Body:
                        {email['body']}

                        ========================================

                    """

        ######################################################
        # Chiamata al modello
        ######################################################

        with st.spinner("Answering..."):

            answer = ask_llm(
                question=query,
                context=context
            )

    ##########################################################
    # Visualizzazione risposta
    ##########################################################

    with st.chat_message("assistant"):

        st.markdown(answer)

        with st.expander("Documents retrieved by the RAG"):

            for item in emails:

                email = item["email"]

                st.markdown(
                    f"""
                        **Similarity:** {item['score']:.3f}

                        **Subject:** {email['subject']}

                        **Sender:** {email['from']}

                        **Date:** {email['date']}

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