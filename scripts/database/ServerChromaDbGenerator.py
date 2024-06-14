import uuid

from scripts.database.DocumentGenerator import DocumentGenerator

import chromadb

document_generator = DocumentGenerator()

class ServerChromaDbGenerator:
    # Define a custom embedding function

    def generateServerChromaDB(self,  collection_name, embedding_function, config_instance):

        # Initialize ChromaDB client
        client = chromadb.HttpClient(host='host.docker.internal', port=8000,
                                     settings=chromadb.Settings(allow_reset=True))
        collections = client.list_collections()
        exists = any(collection.name == collection_name for collection in collections)

        if not exists:
            print(f"ChromaDB does not exist, creating new one - {collection_name}")
            langchain_documents = document_generator.createLangchainDocumentCollectionFromRawDocs(config_instance)

            # Create a collection with the custom embedding function
            collection = client.create_collection(name=collection_name, embedding_function=embedding_function)

            # Add documents to the collection
            for doc in langchain_documents:
                collection.add(ids=[str(uuid.uuid1())], metadatas=doc.metadata, documents=doc.page_content)
        else:
            print(f"ChromaDB collection '{collection_name}' already exists.")

    def main(self):
        print("In main")
        # Call other methods or perform other actions here

