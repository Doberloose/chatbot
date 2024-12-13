import streamlit as st
import os, pinecone, toml
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

if check_variables():

    st.table(data=get_all_metadata_query())

else:
    st.error("La configuration de pinecone n'a pas été effectuée\nVeuillez renseigner les données en cliquant sur le lien ci dessous :")
    st.page_link("pages/config.py", label="configurer")