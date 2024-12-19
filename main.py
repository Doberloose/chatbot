import streamlit as st
import random, time, os, toml, re
from ollama import Client
from langchain_core.runnables import RunnablePassthrough 
from langchain.schema import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import Pinecone
from langchain_ollama import OllamaLLM
from langchain_openai import OpenAIEmbeddings


def check_variables():
    secret_file = f".streamlit/secrets.toml"
    data = toml.load(secret_file)
    secrets = ["url_llm", "open_api_key", "pinecone_api_key"]
    tmp = True
    for secret in secrets:
        val = data.get(secret, "N/A")
        if val == "N/A":
            tmp = False
            break
    if "model" not in st.session_state:
        tmp = False
    else:
        if st.session_state["model"] == "":
            tmp = False
    return tmp


# Fonction pour extraire l'ISIN et créer le filtre
def get_filtre(question):
    isin_match = re.search(r"[A-Z]{2}[0-9]{1}[0-9A-Z]{9}", question)
    isin = isin_match.group() if isin_match else ''
    if isin:
        return {"isin": {"$eq": isin}}
    else:
        return {}
 

# Configuration du retriever avec filtre dynamique
def get_context(input_dict):
    question = input_dict["question"]
    filtre = get_filtre(question)
    return vectorstore_pinecode.similarity_search(
        question,
        k=4,
        filter=filtre
    )


# Définit une fonction générateur pour produire la réponse du modèle par morceaux
def model_res_generator():
    hist = st.session_state["messages"]
    # Démarre un flux de discussion avec le modèle sélectionné et l'historique des messages
    stream = rag_chain.invoke({"question": prompt, "history": hist})
    
    # Produit chaque morceau de la réponse du modèle
    for chunk in stream:
        yield chunk

st.set_page_config(page_title="ChatBot", layout='centered')

if check_variables():

    os.environ["OPENAI_API_KEY"] = st.secrets['open_api_key']
    os.environ["PINECONE_API_KEY"] = st.secrets['pinecone_api_key']
    
    # Initialise l'historique des messages s'il n'existe pas dans l'état de la session
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    
    client = Client(host=st.secrets['url_llm'])

    # Définit le titre de l'application web
    if "model" in st.session_state:
        model = st.session_state['model'].split(":")[0]
    else:
        model = ""
    col1, col2 = st.columns([3, 1], vertical_alignment='bottom')
    with col1:
        st.header(f"Chatbot Ollama ({model})")
    with col2:
        if st.button("effacer historique"):
            st.session_state["messages"] = []

    prompt_template = st.session_state["prompt"]

    prompt_in = PromptTemplate(
        input_variables=["history", "context", "question"],
        template=prompt_template,
    )
    llm = OllamaLLM(
        model=st.session_state["model"],
        base_url=st.secrets['url_llm']  # or your Ollama server URL
    )
    llm_chain = prompt_in | llm | StrOutputParser()

    embedding_model_ = OpenAIEmbeddings()

    index_name = "index-rag"

    # Créer le vectorstore
    vectorstore_pinecode = Pinecone.from_existing_index(
        index_name=index_name,
        embedding=embedding_model_,
        text_key="page_content"
    )


    # Configuration de la chaîne RAG complète
    rag_chain = (
        RunnablePassthrough.assign(context=get_context) | 
        llm_chain
    )

    # Affiche l'historique de la discussion des sessions précédentes
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Récupère l'entrée de l'utilisateur à partir de la zone de saisie de discussion
    if prompt := st.chat_input("Entrez votre message ici..."):
    
        # Ajoute le message de l'utilisateur à l'historique
        st.session_state["messages"].append({"role": "user", "content": prompt})

        # Affiche le message de l'utilisateur dans la discussion
        with st.chat_message("user"):
            st.markdown(prompt)

        # Affiche la réponse de l'assistant dans la discussion
        with st.chat_message("assistant"):
            message = st.write_stream(model_res_generator())
            st.session_state["messages"].append({"role": "assistant", "content": message})

else:
    st.error("La configuration de l'application n'a pas été effectuée\nVeuillez renseigner les données en cliquant sur le lien ci dessous :")
    st.page_link("pages/config.py", label="configurer")

