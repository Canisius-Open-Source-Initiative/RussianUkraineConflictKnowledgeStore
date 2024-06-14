from pathlib import Path

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma

from scripts.database.DocumentGenerator import DocumentGenerator

document_generator = DocumentGenerator()

class LocalChromaDbGenerator:
    def generateLocalChromaDB(self, config_instance):
        embeddings = OpenAIEmbeddings()
        if Path(config_instance.chroma_db_persist).exists():
            print('ChromaDB exists, connecting to it')
            db = Chroma(persist_directory=config_instance.chroma_db_persist, embedding_function=embeddings,
                        collection_name="events")
        else:
            print('ChromaDB does not exist, creating new one')
            langchain_docs = document_generator.createLangchainDocumentCollectionFromRawDocs(config_instance)
            db = Chroma.from_documents(
                langchain_docs, embeddings, collection_name="events", persist_directory=config_instance.chroma_db_persist
            )

        return db