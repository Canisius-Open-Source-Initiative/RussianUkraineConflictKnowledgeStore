import os

from langchain.prompts import PromptTemplate
from scripts.knowledge_store_examples.DataLoader import *
from scripts.knowledge_store_examples.OpenAIUtils import *

class TextAsContext:

    def demo(self, csv_location, openai_key):
        os.environ['OPENAI_API_KEY'] = openai_key
        # Define a prompt template
        prompt = PromptTemplate(
            template="Answer the question based on the provided documents: {documents}\n\nQuestion: {query}\nAnswer:",
            input_variables=["documents", "query"]
        )

        getLLMChain(prompt, 500)

        # Example question
        query = "How does Russia attempt to control the Internet?"

        documents = loadNSAUkraineEventsCSV(csv_location)

        doc_texts = []
        count = 0
        for doc in documents:
          parts = doc.page_content.split("\n")
          text = parts[1]
          doc_texts.append(text)
          count= count + 1
          # Yuck - you do not get much text to pass along this way!
          if(count == 100):
              break

        # Join text
        doc_text = "\n\n".join(doc_texts)

        qa_chain = getLLMChain(prompt, 500)

        # Run the chain
        result = qa_chain.run(documents=doc_text, query=query)

        print(result)