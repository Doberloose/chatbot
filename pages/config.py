import streamlit as st
import toml, time
from ollama import Client

st.title("Configuration technique")

secret_file = f".streamlit/secrets.toml"


def change_secret(prop, val):
    data = toml.load(secret_file)
    data[prop] = val
    with open(secret_file, 'w') as f:
        toml.dump(data, f)


def test_secret(prop):
    data = toml.load(secret_file)
    if data.get(prop, "N/A") == "N/A":
        return False
    else:
        return True


secrets = {
    "url_llm": "URL NGROK",
    "open_api_key": "Clé OPEN API",
    "pinecone_api_key": "Clé pinecone"
}


for secret, display in secrets.items():
    col1, col2 = st.columns([3, 1], vertical_alignment='bottom')
    with col1:
        val_secret = st.text_input(display, value="", type="password")
        if test_secret(secret):
            st.success(f"{display} configuré", icon="✅")
        else:
            st.warning(f"{display} a configurer", icon="⚠️")
        
    with col2:
        if st.button("Appliquer", key=secret):
            change_secret(secret, val_secret)
            if secret == "url_llm":
                time.sleep(1)
            st.rerun()

if test_secret("url_llm"):
    col1, col2 = st.columns([3, 1], vertical_alignment='bottom')
    with col1:
        # Initialise le modèle sélectionné s'il n'existe pas dans l'état de la session
        if "model" not in st.session_state:
            st.session_state["model"] = ""
        # Récupère la liste des modèles disponibles auprès d'Ollama
        client = Client(host=st.secrets['url_llm'])
        models = [model["model"] for model in client.list()["models"]]
        # Permet à l'utilisateur de choisir un modèle dans la liste
        model = st.selectbox("Choisissez votre modèle", models)
        if "model" in st.session_state:
            if st.session_state["model"] != "":
                st.success(f"Modele configuré", icon="✅")
        else:
            st.warning(f"Modele a configurer", icon="⚠️")
    with col2:
        if st.button("Appliquer", key='model_choice'):
            st.session_state["model"] = model
            st.rerun()
