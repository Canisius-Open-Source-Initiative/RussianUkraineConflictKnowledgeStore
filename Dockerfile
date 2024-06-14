FROM python:3.9

WORKDIR /usr/src/app

#COPY requirements.txt ./
#RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir chromadb
RUN pip install --no-cache-dir langchain_community
RUN pip install --no-cache-dir langchain_text_splitters
RUN pip install --no-cache-dir sentence-transformers
RUN pip install --no-cache-dir openai
RUN pip install --no-cache-dir flask
RUN pip install --no-cache-dir ollama
RUN pip install --no-cache-dir pypdf
RUN pip install --no-cache-dir PyPDF2
RUN pip install --no-cache-dir chardet
RUN pip install --no-cache-dir cryptography
RUN pip install --no-cache-dir jq

COPY . .

# Expose the port the Flask app runs on
EXPOSE 5000

# Set the PYTHONPATH environment variable
ENV PYTHONPATH "${PYTHONPATH}:/usr/src/app"

RUN python scripts/rag/rag.py

CMD [ "python", "scripts/rag/rag_query.py" ]

# To build and view the build results run these commands
# docker build -t rag . > build_results.txt 2>&1
# docker run -p 5001:5000 rag
