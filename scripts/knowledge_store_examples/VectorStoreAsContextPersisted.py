import os

from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from scripts.knowledge_store_examples.LocalLLMQueryClient import LocalLLMQueryClient

from scripts.database.LocalChromaDbGenerator import LocalChromaDbGenerator


rag_qc = LocalLLMQueryClient("http://localhost:5001")

class VectorStoreAsContextPersisted:


    def demo(self, config_instance):
        os.environ['OPENAI_API_KEY'] = config_instance.openai_api_key

        # Create ChromaDB
        chromadb_generator = LocalChromaDbGenerator()
        db = chromadb_generator.generateLocalChromaDB(config_instance)

        print("Using model: " + config_instance.openai_chat_model)
        llm = ChatOpenAI(
            model_name="gpt-4-turbo",
            temperature=0.2,
            max_tokens=500,
        )

        retriever = db.as_retriever()


        # Build prompt
        template = """You are an expert consultant helping executive advisors to get relevant information from internal documents.

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
        Context: {context}
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
                print("Answer with web instance of OpenAI's GPT 4 and openai embeddings:")
                print("Answer --------------------------------")
                print(result["result"])
                print("Provenance --------------------------------")
                # Check the source document from where we
                sources = result["source_documents"]
                for source in sources:
                    print(source.metadata)
                print("Answer with local Mistral instance and MiniLM and MPNet embeddings:")
                if rag_qc.check_server() == True:
                    response = rag_qc.send_query(user_input)
                    rag_qc.pretty_print_response(response)
