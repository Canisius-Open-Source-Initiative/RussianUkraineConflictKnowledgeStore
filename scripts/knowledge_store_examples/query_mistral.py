import requests
import json

# A simple script that allows you to query the Rag server that connects to Ollama and Mistral.
def send_query(query):
    url = "http://localhost:5001/query"
    headers = {"Content-Type": "application/json"}
    payload = {"query": query}
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.json()

def main():
    while True:
        query = input("Enter your question (type 'bye' to exit): ")
        if query.lower() == 'bye':
            break
        response = send_query(query)
        print(f"Response:\n{response['response']}")

if __name__ == "__main__":
    main()
