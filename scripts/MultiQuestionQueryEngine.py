import os
import json

from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from scripts.knowledge_store_examples.LocalLLMQueryClient import LocalLLMQueryClient
from scripts.database.LocalChromaDbGenerator import LocalChromaDbGenerator

rag_qc = LocalLLMQueryClient("http://localhost:5001")

class MultiQuestionQueryEngine:

    def process_questions(self, config_instance, questions_file, output_file):
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
        QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

        # Initialize the Retrieval QA Chain
        qa_chain = RetrievalQA.from_chain_type(
            llm,
            retriever=db.as_retriever(search_kwargs={"k": 20}),
            return_source_documents=True,
            chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
        )

        # Load questions from the provided JSON file
        with open(questions_file, 'r') as f:
            questions = json.load(f)['questions']

        # Prepare to store results
        results = []

        for question in questions:
            result_entry = {'question': question}

            # Get the response from the OpenAI LLM with ChromaDB
            result = qa_chain({"query": question})
            print("Answer with web instance of OpenAI's GPT-4:")
            print(result["result"])
            sources = result["source_documents"]
            source_filenames = [os.path.basename(source.metadata['source']) for source in sources]
            result_entry['openai_response'] = result["result"]
            result_entry['openai_source_documents'] = source_filenames

            # Get response from local LLM with MiniLM
            response_minilm = rag_qc.send_minilm_query(question)
            formatted_response_minilm = json.dumps(response_minilm, indent=4)
            response_dict_minilm = json.loads(formatted_response_minilm)
            docs_minilm = response_dict_minilm.get('docs', '').split(',')
            result_entry['minilm_response'] = response_dict_minilm.get('response', '')
            result_entry['minilm_source_documents'] = docs_minilm

            # Get response from local LLM with MPNet
            response_mpnet = rag_qc.send_mpnet_query(question)
            formatted_response_mpnet = json.dumps(response_mpnet, indent=4)
            response_dict_mpnet = json.loads(formatted_response_mpnet)
            docs_mpnet = response_dict_mpnet.get('docs', '').split(',')
            result_entry['mpnet_response'] = response_dict_mpnet.get('response', '')
            result_entry['mpnet_source_documents'] = docs_mpnet

            # Add result for this question
            results.append(result_entry)

        # Write results to a single JSON file
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=4)

        print(f"Results saved to {output_file}")

