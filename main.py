import streamlit as st
import random, time, os, toml
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

st.set_page_config(page_title="ChatBot", layout='centered')

if check_variables():

    os.environ["OPENAI_API_KEY"] = st.secrets['open_api_key']
    os.environ["PINECONE_API_KEY"] = st.secrets['pinecone_api_key']
    
    # Initialise l'historique des messages s'il n'existe pas dans l'état de la session
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    
    client = Client(host=st.secrets['url_llm'])

    # Définit le titre de l'application web
    st.title("Chatbot Ollama")

    historique=''

    prompt_template = """
    <role>
    Vous êtes un assistant d'une équipe du département ALM (gestion des actifs / passifs) dans une entreprise en assurance vie.
    Votre rôle est de répondre à la question entre <question></question> en suivant le contexte entre <contexte></contexte> afin d'assister l'équipe dans le choix des placements à effectuer.
    Le contexte entre <contexte></contexte> contient des informations extraites de document d'informations clés (DIC). Le DIC est un document harmonisé au niveau européen \n
    qui permet de retrouver les informations essentielles sur un placement, sa nature et ses caractéristiques principales.
    Pour Répondre à la question entre <question></question> tu dois absolument suivre les instructions entre <instructions></instructions>.
    </role>

    <instructions>
    La REPONSE doit être concise et rédigée en Français. 
    La REPONSE doit être basée sur le contexte entre <contexte></contexte>.
    La question entre <question></question> doit être interpretée en fonction de l'historique entre <historique></historique>.
    Si le contexte entre <contexte></contexte> ne permet pas de répondre à la question entre <question></question>, réponds "Je ne peux pas répondre à votre demande".
    </instructions>

    <historique>
    {history}
    </historique>

    <contexte>
    {context}
    </contexte>

    <question>
    {question}
    </question>

    REPONSE (La REPONSE doit être concise et rédigée en Français) :::
    """

    prompt_in = PromptTemplate(
        input_variables=["history", "context", "question"],
        template=prompt_template,
    )
    llm = OllamaLLM(
        #model='mistral',
        model=st.session_state["model"].split(":")[0],
        base_url=st.secrets['url_llm']  # or your Ollama server URL
    )
    llm_chain = prompt_in | llm | StrOutputParser()

    embedding_model_ = OpenAIEmbeddings()

    index_name = "index-rag"

    # Créer le vectorstore
    vectorstore = Pinecone.from_existing_index(
        index_name=index_name,
        embedding=embedding_model_,
        text_key="page_content"
    )

    # Créer le retriever
    retriever_p = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={'k': 4}
    )

    rag_chain = RunnablePassthrough.assign(
        context=lambda x: retriever_p.invoke(x["question"])
    ) | llm_chain

    # Définit une fonction générateur pour produire la réponse du modèle par morceaux
    def model_res_generator():
        hist = st.session_state["messages"]
        # Démarre un flux de discussion avec le modèle sélectionné et l'historique des messages
        stream = rag_chain.invoke({"question": prompt, "history": hist})
    
        # Produit chaque morceau de la réponse du modèle
        for chunk in stream:
            yield chunk

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

