import streamlit as st
import pinecone, random, toml
from pinecone import Pinecone, ServerlessSpec


def get_random_chunk(index, top_k=1):
    """
    Récupère un chunk aléatoire depuis un index Pinecone.
    
    Args:
        index: L'index Pinecone
        top_k (int): Nombre de résultats à récupérer (par défaut 1)
        
    Returns:
        dict: Le chunk aléatoire avec ses métadonnées
    """
    # Récupérer des statistiques sur l'index
    stats = index.describe_index_stats()
    total_vectors = stats.total_vector_count
    
    # Générer un vecteur aléatoire de même dimension que l'index
    vector_dim = index.describe_index_stats().dimension
    random_vector = [random.uniform(-1, 1) for _ in range(vector_dim)]
    
    # Faire une requête avec ce vecteur aléatoire
    results = index.query(
        vector=random_vector,
        top_k=top_k,
        include_metadata=True
    )
    
    if not results.matches:
        return None
        
    # Récupérer les IDs des chunks trouvés
    chunk_ids = [match.id for match in results.matches]
    
    # Utiliser fetch pour récupérer les vecteurs complets
    vectors_data = index.fetch(ids=chunk_ids)
    
    # Préparer les résultats en combinant les données
    chunks = []
    for match, vector_id in zip(results.matches, chunk_ids):
        vector_data = vectors_data.vectors.get(vector_id)
        if vector_data:
            chunk_data = {
                'id': match.id,
                'score': match.score,
                'metadata': match.metadata,
                'vector': vector_data.values
            }
            chunks.append(chunk_data)
    
    # Retourner un seul résultat si top_k=1, sinon la liste complète
    return chunks[0] if top_k == 1 else chunks


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


st.set_page_config(page_title="Exemple de vecteur", layout='wide')

_, col, _ = st.columns([1, 2, 1])
with col:
    st.header(f"Exemple de vecteur")


if check_variables():
    col1, col2 = st.columns([1, 2])
    
    pinecone = Pinecone(api_key=st.secrets['pinecone_api_key'])
    index = pinecone.Index("index-rag")
    chunk = get_random_chunk(index, top_k=1)
    if chunk is not None:
        
        with st.container():
            st.markdown("**Metadonnées :**")
            st.markdown(f"* ISIN : {chunk['metadata']['isin']}")
            st.markdown(f"* Produit : {chunk['metadata']['product']}")
            st.markdown(f"* Niveau de risque : {chunk['metadata']['risk_level']}")
        
        with st.container():
            st.markdown("**Contenu :**")
            st.markdown(f"{chunk['metadata']['page_content']}")
        
        with st.container():
            st.markdown("**Vecteur :**")
            st.markdown(f"Score : {chunk['score']}")
            st.write(chunk['vector'])

else:
    st.error("La configuration de pinecone n'a pas été effectuée\nVeuillez renseigner les données en cliquant sur le lien ci dessous :")
    st.page_link("pages/configuration.py", label="configurer")
    