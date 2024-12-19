import streamlit as st
import toml, time
from ollama import Client

st.set_page_config(page_title="Configuration", layout='centered')

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


def format_model(model: str) -> None:
    return model.split(":")[0]


def get_promt(model:str) -> str:

    prompt_defaut = """
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

    prompt_llama = """
        <|begin_of_text|><|start_header_id|>system<|end_header_id|>
        Vous êtes un assistant d'une équipe du département ALM (gestion des actifs / passifs) dans une entreprise en assurance vie.
        Votre rôle est de répondre à la question entre <question></question> en suivant le contexte entre <contexte></contexte> afin d'assister l'équipe dans le choix des placements à effectuer.
        Le contexte entre <contexte></contexte> contient des informations extraites de document d'informations clés (DIC). Le DIC est un document harmonisé au niveau européen \n
        qui permet de retrouver les informations essentielles sur un placement, sa nature et ses caractéristiques principales.
        Pour Répondre à la question entre <question></question> tu dois absolument suivre les instructions entre <instructions></instructions>.

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
        <|eot_id|>

        <|begin_of_text|><|start_header_id|>user<|end_header_id|>
        <question>
        {question}
        </question>
        <|eot_id|>

        <|begin_of_text|><|start_header_id|>assistant<|end_header_id|>
        REPONSE (La REPONSE doit être concise et rédigée en Français) :::
        <|eot_id|>
    """

    prompt_mixtral = """
        <|system|>
        Vous êtes un assistant d'une équipe du département ALM (gestion des actifs / passifs) dans une entreprise en assurance vie.
        Votre rôle est de répondre à la question entre <question></question> en suivant le contexte entre <contexte></contexte> afin d'assister l'équipe dans le choix des placements à effectuer.
        Le contexte entre <contexte></contexte> contient des informations extraites de document d'informations clés (DIC). Le DIC est un document harmonisé au niveau européen \n
        qui permet de retrouver les informations essentielles sur un placement, sa nature et ses caractéristiques principales.
        Pour Répondre à la question entre <question></question> tu dois absolument suivre les instructions entre <instructions></instructions>.

        [INST]La REPONSE doit être concise et rédigée en Français.[/INST]
        [INST]La REPONSE doit être basée sur le contexte entre <contexte></contexte>.[/INST]
        [INST]La question entre <question></question> doit être interpretée en fonction de l'historique entre <historique></historique>.[/INST]
        [INST]Si le contexte entre <contexte></contexte> ne permet pas de répondre à la question entre <question></question>, réponds "Je ne peux pas répondre à votre demande".[/INST]

        <historique>
        {history}
        </historique>

        <contexte>
        {context}
        </contexte>
        </s>

        <|user|>
        <question>
        {question}
        </question>
        </s>

        <|assistant|>
        REPONSE [INST]La REPONSE doit être concise et rédigée en Français[/INST] :::
    """

    prompt_model = {
        'mixtral:8x7b': prompt_mixtral,
        'llama3.1:latest': prompt_llama
    }

    return prompt_model.get(model, prompt_defaut)


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
        model = st.selectbox("Choisissez votre modèle", models, format_func=format_model)
        if "model" in st.session_state:
            if st.session_state["model"] != "":
                st.success(f"Modele configuré", icon="✅")
        else:
            st.warning(f"Modele a configurer", icon="⚠️")
    with col2:
        if st.button("Appliquer", key='model_choice'):
            st.session_state["model"] = model
            st.session_state["prompt"] = get_promt(model)
            st.rerun()
if "prompt" in st.session_state:
    with st.container(border=True):
        st.markdown("Prompt utilisé : ")
        st.write(st.session_state["prompt"]) 