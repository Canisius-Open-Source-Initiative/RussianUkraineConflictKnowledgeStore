import logging
import os

import chromadb
from chromadb.config import Settings
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain_community.vectorstores import Chroma

from scripts.Config import Config
from scripts.embedding_functions.MPNetCustomEmbeddingFunction import MPNetCustomEmbeddingFunction
from scripts.embedding_functions.MiniLMCustomEmbeddingFunction import MiniLMCustomEmbeddingFunction


# Some of the code found here kindly taken from this article:
# https://medium.com/@mbrazel/open-source-self-hosted-rag-llm-server-with-chromadb-docker-ollama-7e6c6913da7a

def create_chroma_db(embedding_function, collection_name):
    chroma_client = chromadb.HttpClient(host='host.docker.internal', port=8000, settings=Settings(allow_reset=True))
    db = Chroma(
        client=chroma_client,
        collection_name=collection_name,
        embedding_function=embedding_function,
    )
    return db


def Extract_context(query, client):
    fullcontent = ''
    fullcontent = '. '.join([fullcontent, 'Client 1'])

    # Increase to 20 documents
    docs = client.similarity_search(query, k=20)

    # Filter documents based on a hypothetical similarity score threshold
    threshold = 0.7
    filtered_docs = [doc for doc in docs if doc.metadata.get('similarity_score', 1.0) >= threshold]

    doc_names = set()

    for doc in filtered_docs:
        fullcontent = '. '.join([fullcontent, doc.page_content])
        doc_metadata = doc.metadata
        doc_name = doc_metadata.get('source', 'Unknown')  # or any other identifier you prefer
        filename = os.path.basename(doc_name)
        # Names represent the provenance
        doc_names.add(filename)

    return fullcontent, list(doc_names)


def Extract_context_prior(query, client):

    fullcontent = ''

    fullcontent = '. '.join([fullcontent, 'Client 1'])
    docs = client.similarity_search(query, k=10)
    doc_names = set()

    for doc in docs:
        fullcontent = '. '.join([fullcontent, doc.page_content])
        doc_metadata = doc.metadata
        doc_name = doc_metadata.get('source', 'Unknown')  # or any other identifier you prefer
        # Names represent the provenance
        doc_names.add(doc_name)

    return fullcontent, list(doc_names)



# Prompt kindly reused with permission from Matt Brazel: https://medium.com/@mbrazel/open-source-self-hosted-rag-llm-server-with-chromadb-docker-ollama-7e6c6913da7a
def get_system_message_rag(content):
    return f"""You are an expert consultant helping executive advisors to get relevant information from internal documents.

    Generate your response by following the steps below:
    1. Recursively break down the question into smaller questions.
    2. For each question/directive:
        2a. Select the most relevant information from the context in light of the conversation history.
    3. Generate a draft response using selected information.
    4. Remove duplicate content from draft response.
    5. Generate your final response after adjusting it to increase accuracy and relevance.
    6. Do not try to summarise the answers, explain it properly.
    6. Only show your final response! 

    Constraints:
    1. DO NOT PROVIDE ANY EXPLANATION OR DETAILS OR MENTION THAT YOU WERE GIVEN CONTEXT.
    2. Don't mention that you are not able to find the answer in the provided context.
    3. Don't make up the answers by yourself.
    4. Try your best to provide answer from the given context.

    CONTENT:
    {content}
    """

def get_ques_response_prompt(question):
    return f"""
    ==============================================================
    Based on the above context, please provide the answer to the following question:
    {question}
    """

from ollama import Client

def generate_rag_response(content,question):
    logger.debug("Using a basic text implementation")
    client = Client(host='http://host.docker.internal:11434')
    stream = client.chat(model='mistral', messages=[
    {"role": "system", "content": get_system_message_rag(content)},
    {"role": "user", "content": get_ques_response_prompt(question)}
    ],stream=True)
    logger.debug(get_system_message_rag(content))
    logger.debug(get_ques_response_prompt(question))
    logger.debug("####### THINKING OF ANSWER............ ")
    full_answer = ''
    for chunk in stream:
        logger.debug(chunk['message']['content'], end='', flush=True)
        full_answer =''.join([full_answer,chunk['message']['content']])

    return full_answer


from flask import Flask, request

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/queryminilm', methods=['POST'])
def respond_to_minilm_query():
    config_instance = Config("scripts/config_docker.ini")
    if request.method == 'POST':
        data = request.get_json()
        # Assuming the query is sent as a JSON object with a key named 'query'
        query = data.get('query')

        # Extract context using ChromaDB
        # Create clients with different embedding models
        minilm_embedding_function = MiniLMCustomEmbeddingFunction(config_instance.chroma_db_minilm_model_name)
        client_miniLM = create_chroma_db(minilm_embedding_function, config_instance.chroma_db_minilm_collection_name)

        context, doc_names = Extract_context(query, client_miniLM)
        logger.debug("About to call generate_rag_response")
        # Generate response using the context and the query
        response = generate_rag_response(context, query)
        logger.debug(response)
        # Include document names in the response
        doc_names_str = ",".join(doc_names)
        return {"response": response, "docs":doc_names_str}

@app.route('/querympnet', methods=['POST'])
def respond_to_mpnet_query():
    config_instance = Config("scripts/config_docker.ini")
    if request.method == 'POST':
        data = request.get_json()
        # Assuming the query is sent as a JSON object with a key named 'query'
        query = data.get('query')

        # Extract context using ChromaDB
        # Create clients with different embedding models
        mpnet_embedding_function = MPNetCustomEmbeddingFunction(config_instance.chroma_db_mpnet_model_name)
        client_mpnet = create_chroma_db(mpnet_embedding_function, config_instance.chroma_db_mpnet_collection_name)

        context, doc_names = Extract_context(query, client_mpnet)
        logger.debug("About to call generate_rag_response")
        # Generate response using the context and the query
        response = generate_rag_response(context, query)
        logger.debug(response)
        # Include document names in the response
        doc_names_str = ",".join(doc_names)
        return {"response": response, "docs":doc_names_str}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    logger.debug("Flask server indeed started!")