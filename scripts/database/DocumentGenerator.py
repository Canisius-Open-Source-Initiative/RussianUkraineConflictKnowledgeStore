import os
import PyPDF2
from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFDirectoryLoader, DirectoryLoader, JSONLoader
from scripts.knowledge_store_examples.DataLoader import loadNSAUkraineEventsCSV

class DocumentGenerator:

    def cleanInvalidPdfs(self, file_directory):
        print("Cleaning: " + file_directory)
        for dirpath, dirnames, filenames in os.walk(file_directory):
                for filename in filenames:
                    filename_complete = os.path.join(dirpath, filename)
                    #print(filename_complete)
                    try:
                        with open(filename_complete, 'rb') as pdf_file:
                            pdf_reader = PdfReader(pdf_file)
                            # No need to perform operations with the PDF file
                            # Simply seeing if it is a well formed PDF
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
        loader = PyPDFDirectoryLoader(pdf_files_directory)
        pages = loader.load_and_split()

        for page in pages:
            print(page)

        return pages

    def createLangchainDocumentCollectionFromRawDocs(self, config_instance):
        print(config_instance.pdfs_folder)
        # 1. You may have downloaded some invalid PDFs.  Remove them! Comment
        print("About to clean PDFs")
        self.cleanInvalidPdfs(config_instance.pdfs_folder)
        loader = PyPDFDirectoryLoader(os.path.join(config_instance.pdfs_folder, ''))
        pdf_pages = loader.load_and_split()
        print("Loaded PDFs")

        langchain_docs = self.generateJsonLangChainDocs(config_instance.jsons_folder)
        langchain_docs.extend(pdf_pages)
        print(len(langchain_docs))
        eventsDocs = loadNSAUkraineEventsCSV(config_instance.nsa_csv_timeline)
        langchain_docs.extend(eventsDocs)
        print("added Events docs")
        print(len(langchain_docs))

        return langchain_docs

    def generateJsonLangChainDocs(self, jsons_folder):
        # Link to JSON loading: https://python.langchain.com/docs/modules/data_connection/document_loaders/json
        json_loader = DirectoryLoader(jsons_folder, loader_cls=JSONLoader,
                                      loader_kwargs={'jq_schema': '.text'})
        # json_loader = JSONLoader(txt_files_directory, jq_schema='.text')
        json_docs = json_loader.load()
        print("Loaded JSON docs")
        splitter = CharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=50,
            separator=" "
        )
        langchain_docs = splitter.split_documents(json_docs)
        print(len(langchain_docs))
        return langchain_docs