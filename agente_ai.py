import streamlit as st

from email_utils import search_documents
from llm import ask_llm


####
# Configurazione pagina
####

st.set_page_config(
    page_title="Document Retrieval assistant",
    page_icon="�",
    layout="wide"
)

####
# Stato della chat
####

if "messages" not in st.session_state:
    st.session_state.messages = []

####
# Titolo
####

st.title("� Document Retrieval assistant")

st.write(
    "Smart retrieval of your documents"
)

####
# Visualizzazione cronologia
####

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

####
# Input utente
####

query = st.chat_input(
    "Ask a question here"
)

####
# Elaborazione
####

if query:

    
    # Messaggio utente
    

    st.session_state.messages.append(
        {
            "role": "user",
            "content": query
        }
    )

    with st.chat_message("user"):
        st.markdown(query)

    
    # Ricerca nel database vettoriale
    

    with st.spinner("Document research..."):

        documents = search_documents(query)

    
    # Nessun risultato
    

    if len(documents) == 0:

        answer = (
            "No relevant documents found for the request."
        )

    else:

        
        # Costruzione del contesto
        

        context = ""

        for item in documents:

            score = item["score"]
            doc = item["email"] if "email" in item else item["pdf"]
        
            context += f"""
                        ========================================

                        Similarity: {score:.3f}

                        context_document:
                        {doc}

                        ========================================

                    """
        # Chiamata al modello
        

        with st.spinner("Answering..."):

            answer = ask_llm(
                question=query,
                context=context
            )

    
    # Visualizzazione risposta
    

    with st.chat_message("assistant"):

        st.markdown(answer)

        with st.expander("Documents retrieved by the RAG"):

            for item in documents:

                doc = item["email"] if "email" in item.keys() else item["pdf"]
                
                st.markdown(
                    f"""
                        **Similarity:** {item['score']:.3f}

                        **Context Document:** {doc}

                        ---
                    """
                )

    
    # Salvataggio cronologia
    

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )