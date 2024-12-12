import streamlit as st
import random
import time

# Fonction pour simuler une réponse avec un délai
def response_generator():
    # Choisir une réponse aléatoire parmi une liste
    response = random.choice(
        [
            "Bonjour ! Comment puis-je vous aider aujourd'hui ?",
            "Salut ! Y a-t-il quelque chose que je peux faire pour vous ?",
            "Avez-vous besoin d'aide ?",
        ]
    )
    # Afficher chaque mot avec un petit délai pour simuler un flux
    for word in response.split():
        yield word + " "
        time.sleep(0.05)

st.title("Chatbot documentation financière")

# Initialiser l'historique des messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Afficher les messages de l'historique lors du rechargement de l'application
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accepter l'entrée utilisateur
if prompt := st.chat_input("Message"):
    # Ajouter le message utilisateur à l'historique
    st.session_state.messages.append({"role": "human", "content": prompt})
    # Afficher le message utilisateur dans le conteneur de messages
    with st.chat_message("user"):
        st.markdown(prompt)

    # Afficher la réponse de l'assistant dans le conteneur de messages
    with st.chat_message("assistant"):
        response = st.write_stream(response_generator())
    # Ajouter la réponse de l'assistant à l'historique
    st.session_state.messages.append({"role": "ai", "content": response})
