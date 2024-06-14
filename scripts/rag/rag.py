from langchain_community.embeddings import SentenceTransformerEmbeddings

from scripts.Config import Config
from scripts.embedding_functions.MPNetCustomEmbeddingFunction import MPNetCustomEmbeddingFunction
from scripts.embedding_functions.MiniLMCustomEmbeddingFunction import MiniLMCustomEmbeddingFunction
from scripts.database.ServerChromaDbGenerator import ServerChromaDbGenerator

import sys
import os

from scripts.rag.rag_query import create_chroma_db

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Create an instance of the ServerChromaDbGenerator and make the collection in the container if necessary
# For this to work - you need a Docker instance of ChromaDB server running
# docker run -d -p 8000:8000 -v chromadb_data:/app/data -e PERSIST_DIRECTORY=/app/data chromadb/chroma
# And do this to run the RAG server
# docker run -d -p 5001:5000 rag

scdbg = ServerChromaDbGenerator()
config_instance = Config("scripts/config_docker.ini")
mpnet_embedding_function = MPNetCustomEmbeddingFunction(config_instance.chroma_db_mpnet_model_name)
scdbg.generateServerChromaDB(config_instance.chroma_db_mpnet_collection_name, mpnet_embedding_function, config_instance)
minilm_embedding_function = MiniLMCustomEmbeddingFunction(config_instance.chroma_db_minilm_model_name)
scdbg.generateServerChromaDB(config_instance.chroma_db_minilm_collection_name, minilm_embedding_function, config_instance)

client_miniLM = create_chroma_db(minilm_embedding_function, config_instance.chroma_db_minilm_collection_name)
client_mpnet = create_chroma_db(mpnet_embedding_function, config_instance.chroma_db_mpnet_collection_name)

dbs = [client_miniLM, client_mpnet]
for db in dbs:
    query = "What cyber attacks have happened in the Ukraine?"
    docs = db.similarity_search(query)
    print(docs[0].page_content)
