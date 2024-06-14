import concurrent
import concurrent.futures
import json
import os
import re
import threading
from datetime import datetime
from ssl import SSLError
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--no-sandbox')

_lock = threading.Lock()
countfile = 0


class HtmlDownloader:

    def get_domain_from_url(self,url):
        parsed_url = urlparse(url)
        return parsed_url.netloc

    def find_html_urls(self, file_path):
        with open(file_path, 'r') as file:
            content = file.read()
            # Use regular expression to find URLs with ".pdf" extension
            non_pdf_urls = re.findall(r'\bhttps://\S+(?<!\.pdf)\b', content)
            for url in non_pdf_urls:
                print(url)
            return non_pdf_urls

    def tranlsateUrlListIntoSet(self, urlList):
        url_set = {}
        for url in urlList:
            if url in url_set:
                continue
            else:
                url_set[url] = 'T'
        return url_set

    def process_url(self, url_key):
        if url_key.startswith('https://'):
            try:
                response = requests.get(url_key)
                response.raise_for_status()  # Raises HTTPError for bad requests (4xx and 5xx status codes)
                self.download_html_page_as_txt(url_key, response)
            except SSLError as ssl_error:
                print(f"SSL Error occurred: {ssl_error}")
                # Handle SSL error gracefully (e.g., log the error or take other appropriate action)
            except requests.exceptions.HTTPError as http_error:
                print(f"HTTP Error occurred: {http_error}")
                # Handle HTTP error gracefully
            except requests.exceptions.RequestException as request_exception:
                print(f"Request Exception occurred: {request_exception}")
                # Handle other request exceptions gracefully
            except Exception as general_exception:
                print(f"An unexpected error occurred: {general_exception}")
                # Handle other unexpected exceptions gracefully
            else:
                # Code to run if no exceptions were raised
                print("Request successful!")

    def download_html_page_as_txt(self, url, response):
        with _lock:
            _, file_extension = os.path.splitext(url)
            current_directory = os.getcwd()

            # Print the current working directory
            global countfile
            countfile += 1
            txt_url = url
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                main_content_tags = ['p', 'article']
                main_content = []
                for tag in main_content_tags:
                    main_content.extend(soup.find_all(tag))

                # Extracted text
                extracted_text = ' '.join([element.get_text() for element in main_content])

                # Add URL and date as metadata
                metadata = {
                    'url': url,
                    'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                data = {
                    'metadata': metadata,
                    'text': extracted_text
                }

                # Convert the data to a JSON string
                json_data = json.dumps(data, indent=2)

                # File naming
                domain = self.get_domain_from_url(url)
                file_name = f'text-{countfile}-{domain}.json'

                # Write the JSON data to the file
                with open(file_name, 'w') as file:
                    file.write(json_data)

            else:
                print(f"Failed to fetch the webpage. Status code: {response.status_code}")

    def downloadHtmlsAsTextFiles(self, eventTimelineCsv, output_folder):
        urls = self.find_html_urls(eventTimelineCsv)
        url_set = self.tranlsateUrlListIntoSet(urls)
        os.chdir(output_folder)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(self.process_url, url_set.keys())
