from typing import List

from chromadb import EmbeddingFunction
from sentence_transformers import SentenceTransformer


class MiniLMCustomEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model_name: str):
        super().__init__()
        self.model = SentenceTransformer(model_name)

    def __call__(self, input: List[str]) -> List[List[float]]:
        # Use the Sentence Transformers model for embeddings
        embeddings_ndarray = self.model.encode(input)  # Returns an ndarray
        embeddings_list = embeddings_ndarray.tolist()  # Convert ndarray to list
        return embeddings_list

    def embed_query(self, query: str) -> List[float]:
        """
        Embeds a query using the Sentence Transformers model.

        Args:
            query (str): The input query to embed.

        Returns:
            List[float]: A list of embeddings.
        """
        embeddings_ndarray = self.model.encode(query)  # Returns an ndarray
        embeddings_list = embeddings_ndarray.tolist()  # Convert ndarray to list
        return embeddings_list


# Usage example
if __name__ == "__main__":
    embedding_model_name = "all-mpnet-base-v2"  # Specify your model name
    embedder = MyEmbeddingFunction(embedding_model_name)

    # Test embedding a query
    query = "This is a test query."
    query_embedding = embedder.embed_query(query)
    print("Query Embedding:", query_embedding)

    # Test embedding documents
    documents = ["This is a test document.", "This is another test document."]
    documents_embedding = embedder(documents)
    print("Documents Embedding:", documents_embedding)
