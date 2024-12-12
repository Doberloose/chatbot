import streamlit as st
import toml

st.title("Configuration technique")

secret_file = f".streamlit/secrets.toml"


def change_secret(prop, val):
    data = toml.load(secret_file)
    data[prop] = val
    with open(secret_file, 'w') as f:
        toml.dump(data, f)


def get_secret(prop):
    data = toml.load(secret_file)
    return data.get(prop, "N/A")


secrets = {
    "url_llm": "URL NGROK",
    "open_api_key": "Clé OPEN API",
    "pinecone_api_key": "Clé pinecone"
}


for secret, display in secrets.items():
    col1, col2 = st.columns([3, 1], vertical_alignment='bottom')
    with col1:
        url_llm = st.text_input(display, value="")
        st.text(f"Valeur présente dans la configuration : {get_secret(secret)}")
        
    with col2:
        if st.button("Appliquer", key=secret):
            change_secret(secret, url_llm)
            st.rerun()
