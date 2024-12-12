import streamlit as st
import toml

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
        url_llm = st.text_input(display, value="")
        if test_secret(secret):
            st.success(f"{display} configuré", icon="✅")
        else:
            st.warning(f"{display} a configurer", icon="⚠️")
        
    with col2:
        if st.button("Appliquer", key=secret):
            change_secret(secret, url_llm)
            st.rerun()
