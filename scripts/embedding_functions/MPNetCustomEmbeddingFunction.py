import chromadb
from chromadb import Embeddings, Documents, EmbeddingFunction
from sentence_transformers import SentenceTransformer
from chromadb.config import Settings
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain_community.vectorstores import Chroma

class MPNetCustomEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        # Use the Sentence Transformers model for embeddings
        embeddings_ndarray = self.model.encode(input)  # Returns an ndarray
        embeddings_list = embeddings_ndarray.tolist()  # Convert ndarray to list
        return embeddings_list

    def __init__(self, model_Name: str):
        self.model = SentenceTransformer(model_Name)
        super().__init__()

    def embed_query(self, query: str) -> Embeddings:
        """
        Embeds a query using the Sentence Transformers model.

        Args:
            query (str): The input query to embed.

        Returns:
            Embeddings: A list of embeddings.
        """
        embeddings_ndarray = self.model.encode(query)  # Returns an ndarray
        embeddings_list = embeddings_ndarray.tolist()  # Convert ndarray to list
        return embeddings_list