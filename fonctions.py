from langchain.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from transformers import pipeline
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


def ask_ai(question, contexte, historique=''):
    llm = HuggingFacePipeline(pipeline=pipe)
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

    REPONSE :::
    """

    prompt = PromptTemplate(
        input_variables=["history", "context", "question"],
        template=prompt_template,
    )

    llm_chain = prompt | llm | StrOutputParser()

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={'k': 4}
    )

    rag_chain = RunnablePassthrough.assign(
        context=lambda x: retriever.get_relevant_documents(x["question"])

    ) | llm_chain


def ajouter_a_historique(conversation_historique, nouvelle_conv):
    if conversation_historique:
        historique_mise_a_jour = conversation_historique + "\n\n" + nouvelle_conv
    else:
        historique_mise_a_jour = nouvelle_conv
    
    mots = historique_mise_a_jour.split()
    nombre_mots = len(mots)
    
    if nombre_mots > 1000:
        mots_a_garder = mots[-1000:]
        historique_mise_a_jour = " ".join(mots_a_garder)
    
    return historique_mise_a_jour

def avoir_une_reponse(question, historique):
    question = 'query:' + question
    reponse = rag_chain.invoke({"question": question, "history": historique})

    reponse_finale = reponse.split(":::")[-1].strip()
    context = reponse.split('<contexte>')[1].split('</contexte>')[0]
    nouvelle_conv = f"Question : {question}\nRéponse : {reponse_finale}"
    
    historique = ajouter_a_historique(historique, nouvelle_conv)
    return historique, reponse_finale , reponse
