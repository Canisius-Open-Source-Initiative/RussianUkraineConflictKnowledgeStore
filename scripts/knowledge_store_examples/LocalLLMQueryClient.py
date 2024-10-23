import requests
import json


class LocalLLMQueryClient:
    def __init__(self, ollama_server_url):
        self.server_url = ollama_server_url
        if not self.check_server():
            raise ConnectionError("Server is not accessible.")

    def check_server(self):
        try:
            url = f"{self.server_url}/queryminilm"
            response = requests.get(url)
            if response.status_code == 405:
                print("Server is accessible.")
                return True
            else:
                print("Server returned a non-405 status code.")
                return False
        except requests.ConnectionError:
            print("Failed to connect to the server.")
            return False

    def send_minilm_query(self, query):
        url = f"{self.server_url}/queryminilm"
        headers = {"Content-Type": "application/json"}
        payload = {"query": query}
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        return response.json()

    def send_mpnet_query(self, query):
        url = f"{self.server_url}/querympnet"
        headers = {"Content-Type": "application/json"}
        payload = {"query": query}
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        return response.json()

    def pretty_print_response(self, response):
        formatted_response = json.dumps(response, indent=4)
        response_dict = json.loads(formatted_response)
        response_str = response_dict['response']
        print("\nResponse:\n")
        print(response_str)
        response_str = response_dict['docs']
        print("\nResponse:\n")
        print(response_str)


