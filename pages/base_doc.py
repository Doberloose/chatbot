import streamlit as st
import os, pinecone, toml, fitz, re
from pinecone import Pinecone, ServerlessSpec
from tqdm.auto import tqdm
from langchain.embeddings import OpenAIEmbeddings


@st.cache_data
def get_all_metadata_query(batch_size=1000):
    with st.spinner('Récupération des documents'):
        pinecone = Pinecone(api_key=st.secrets['pinecone_api_key'])
        index = pinecone.Index("index-rag")

        all_metadata = []
        # Query avec un vecteur nul et un filtre vide pour tout récupérer
        results = index.query(
            vector=[0] * index.describe_index_stats()['dimension'],  # vecteur nul
            top_k=batch_size,
            include_metadata=True,
            include_values=False  # on ne veut que les métadonnées, pas les vecteurs
        )
        for match in results['matches']:
            if 'metadata' in match:
                all_metadata.append(match['metadata']['source'])
        return list(set(all_metadata))


def check_variables():
    secret_file = f".streamlit/secrets.toml"
    data = toml.load(secret_file)
    secrets = ["pinecone_api_key"]
    tmp = True
    for secret in secrets:
        val = data.get(secret, "N/A")
        if val == "N/A":
            tmp = False
            break
    return tmp


def process_file(fic_in):
    #doc = fitz.open(fic_in)
    doc = fitz.open(stream=fic_in.read(), filetype="pdf")
    text = ""
    for page in doc:
        text+=page.get_text()
    
    text_pdf = clean_up_text(text)

    # Extract metadata
    product, isin, risk_level = extract_metadata(text_pdf)

    return product, isin, risk_level, text_pdf


def clean_up_text(content: str) -> str:
    # Correction des mots avec trait d'union interrompus par la nouvelle ligne
    content = re.sub(r'(\w+)-\n(\w+)', r'\1\2', content)

    # Supprimer des motifs et des caractères indésirables spécifiques
    unwanted_patterns = [
        "  —", "——————————", "—————————", "—————",
        r'\\u[\dA-Fa-f]{4}', r'\uf075', r'\uf0b7'
    ]
    for pattern in unwanted_patterns:
        content = re.sub(pattern, "", content)

    # Corriger les mots avec trait d'union mal espacés
    content = re.sub(r'(\w)\s*-\s*(\w)', r'\1-\2', content)
    content = re.sub(r'^[\*\-\u2022]', '', content)
    
    return content


def extract_metadata(text: str):
    """
    Extract metadata (product name, ISIN, risk level) from PDF text.

    Args:
        text (str): Cleaned text from PDF

    Returns:
        Tuple[str, str, int]: Product name, ISIN code, and risk level
    """
    product, isin, risk_level = '', '', -1

    # Extract risk level using regex pattern
    # Looks for variations of "risk level" or "risk category" followed by a number
    risk_pattern = r"(?:(?:niveau|classe|catégorie)\sde\srisque(?:\sde\sce\scompartiment\sest\sde)?|indicateur\sde\srisque\sde\sniveau|(?:est\sclassé(?:\sdans\sla)?|appartient\sà\sla)\scat[ée]gorie)\s(\d+)"
    risk_match = re.search(risk_pattern, text)
    risk_level = int(risk_match.group(1)) if risk_match else -1

    # Extract ISIN code (format: 2 letters, 1 number, 9 alphanumeric characters)
    isin_match = re.search(r"[A-Z]{2}[0-9]{1}[0-9A-Z]{9}", text)
    isin = isin_match.group() if isin_match else ''

    # Find product name in the sentence containing ISIN
    if isin:
        sentences = re.split('(?<=[.!?])\s+', text)
        for sentence in sentences:
            if isin in sentence:
                product = sentence.strip()
                break

    return product, isin, risk_level


st.set_page_config(page_title="Base doc", layout='wide')


if check_variables():
    col1, col2 = st.columns([1, 2])
    with col1:
        st.table(data=get_all_metadata_query())
    with col2:
        fic_in = st.file_uploader("Nouveau fichier à charger", type=['pdf'])
        if fic_in:
            name_fic_in = fic_in.name
            product, isin, risk_level, text_pdf = process_file(fic_in)
            st.markdown(f"**Nom du produit :** {product}")
            st.markdown(f"**ISIN :** {isin}")
            st.markdown(f"**Code risque :** {risk_level}")
            st.markdown(f"**Corps du PDF :**\n{text_pdf}")
        else:
            name_fic_in = None

else:
    st.error("La configuration de pinecone n'a pas été effectuée\nVeuillez renseigner les données en cliquant sur le lien ci dessous :")
    st.page_link("pages/config.py", label="configurer")