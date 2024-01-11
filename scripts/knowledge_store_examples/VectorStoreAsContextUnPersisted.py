import os

from langchain.embeddings.openai import OpenAIEmbeddings
from scripts.knowledge_store_examples.DataLoader import *
from langchain.vectorstores import Chroma
from langchain.chains import  RetrievalQA
from langchain.chat_models import ChatOpenAI


class VectorStoreAsContextUnPersisted:

    def demo(self, csv_location, openai_key):

        os.environ['OPENAI_API_KEY'] = openai_key
        # Initialize OpenAIEmbeddings
        embeddings = OpenAIEmbeddings()

        documents = loadNSAUkraineEventsCSV(csv_location)
        # Create ChromaDB
        embeddings = OpenAIEmbeddings()
        db = Chroma.from_documents(documents, embeddings)
        llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.,
            max_tokens=500,
        )


        retriever = db.as_retriever()

        qa_chain = RetrievalQA.from_chain_type(llm=llm,
                                               retriever=retriever,)

        query = "What is the IT Army?"
        response = qa_chain.run(query)
        #https://getmetal.io/posts/14-agents-with-langchain
        print(response)
