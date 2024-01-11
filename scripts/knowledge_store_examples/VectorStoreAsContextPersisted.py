import PyPDF2
from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import JSONLoader
from langchain_core.prompts import PromptTemplate
from scripts.knowledge_store_examples.DataLoader import *
import os
from langchain.vectorstores import Chroma
from langchain.chains import   RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import  PyPDFDirectoryLoader, DirectoryLoader, TextLoader
from pathlib import Path


class VectorStoreAsContextPersisted:

    def cleanInvalidPdfs(self, file_directory):
        print("Cleaning: " + file_directory)
        for dirpath, dirnames, filenames in os.walk(file_directory):
                for filename in filenames:
                    filename_complete = os.path.join(dirpath, filename)
                    #print(filename_complete)
                    try:
                        with open(filename_complete, 'rb') as pdf_file:
                            pdf_reader = PdfReader(pdf_file)
                            # Perform operations with the PDF file
                            # ...
                    except (PdfReadError, PyPDF2.errors.PdfReadError) as e:
                        print(f"Error reading PDF file '{filename_complete}': {e}")
                        # Handle the error or log it
                        # Remove the file that caused the exception
                        os.remove(filename_complete)
                    except Exception as e:
                        print(f"An unexpected error occurred while processing '{filename_complete}': {e}")
                        # Handle other unexpected exceptions

    def loadPDFiles(self, pdf_files_directory):
        # Get a list of all files in the directory
        pdf_files = [os.path.join(pdf_files_directory, file) for file in os.listdir(pdf_files_directory) if file.lower().endswith('.pdf')]
        loader = PyPDFDirectoryLoader(pdf_files_directory);
        pages = loader.load_and_split()

        for page in pages:
            print(page)

        return pages

    def generateChromaDB(self, chroma_db_location, pdf_files_directory, json_files_directory, csv_timeline_location):
        embeddings = OpenAIEmbeddings()
        if Path(chroma_db_location).exists():
            print('ChromaDB exists, connecting to it')
            db = Chroma(persist_directory=chroma_db_location, embedding_function=embeddings, collection_name="events")
        else:
            print('ChromaDB does not exist, creating new one')
            print(pdf_files_directory)
            # 1. You may have downloaded some invalid PDFs.  Remove them! Comment
            print("About to clean PDFs")
            self.cleanInvalidPdfs(pdf_files_directory)

            loader = PyPDFDirectoryLoader(pdf_files_directory+ "/");
            pdf_pages = loader.load_and_split()
            print("Loaded PDFs")

            # Link to JSON loading: https://python.langchain.com/docs/modules/data_connection/document_loaders/json
            json_loader = DirectoryLoader(json_files_directory, loader_cls=JSONLoader, loader_kwargs = {'jq_schema': '.text'})

            #json_loader = JSONLoader(txt_files_directory, jq_schema='.text')
            json_docs = json_loader.load()
            print("Loaded JSON docs")

            splitter = CharacterTextSplitter(
                chunk_size=2000,
                chunk_overlap=50,
                separator=" "
            )

            json_pages = splitter.split_documents(json_docs)

            print(len(json_pages))
            json_pages.extend(pdf_pages)
            print(len(json_pages))
            eventsDocs = loadNSAUkraineEventsCSV(csv_timeline_location)
            json_pages.extend(eventsDocs)
            print("added Events docs")
            print(len(json_pages))
            #TODO - Redo this with provenance: db = Chroma.from_documents(texts, openai.Embeddings(), store_provenance=True)
            db = Chroma.from_documents(
                json_pages, embeddings, collection_name="events", persist_directory=chroma_db_location
            )

        return db

    def demo(self, chroma_db_location, pdf_files_directory, txt_files_directory, csv_timeline_location, openai_key):
        os.environ['OPENAI_API_KEY'] = openai_key

        # Create ChromaDB
        db = self.generateChromaDB(chroma_db_location, pdf_files_directory, txt_files_directory, csv_timeline_location)

        llm = ChatOpenAI(
            model_name="gpt-3.5-turbo-1106",
            temperature=0.3,
            max_tokens=500,
        )


        retriever = db.as_retriever()

        # Build prompt
        template = """Use the following pieces of context to answer the question at the end. You knowledge store is 
        populated with a set of documents about the Russian and Ukraine conflict from 2014 until May of 2023.  It contains 
        lots of information about the conflict.  Consult this knowledge store and do your best to answer questions.  Try
        and use as manu documents as possible if your answer. 
        If you don't know the answer, just say that you don't know, don't try to make up an answer. 
        {context}
        Question: {question}
        Helpful Answer:"""
        QA_CHAIN_PROMPT = PromptTemplate.from_template(template)# Run chain
        qa_chain = RetrievalQA.from_chain_type(
            llm,
            retriever=db.as_retriever(),
            return_source_documents=True,
            chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
        )
        print("---------------------------------------------------------------------")
        print("Welcome to the Russian and Ukraine knowledge store.  it contains 100s of documents related to the conflict.")
        print("The documents were referenced by this human curated timeline found here:")
        print("https://nsarchive.gwu.edu/document/29562-cyber-vault-ukraine-timeline")
        print("---------------------------------------------------------------------")

        while True:
            user_input = input("Enter your question: (type 'exit' to stop): ")

            if user_input.lower() == 'exit':
                print("Exiting the loop.")
                break
            else:
                result = qa_chain({"query": user_input})
                # Check the result of the query
                print("Answer --------------------------------")
                print(result["result"])
                print("Provenance --------------------------------")
                # Check the source document from where we
                sources = result["source_documents"]
                for source in sources:
                    print(source.metadata)
