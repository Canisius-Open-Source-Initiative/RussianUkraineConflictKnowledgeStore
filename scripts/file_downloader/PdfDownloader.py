import os
import re
import requests

class PdfDownloader:

    def find_pdf_urls(self, file_path):
        with open(file_path, 'r') as file:
            content = file.read()
            # Use regular expression to find URLs with ".pdf" extension
            pdf_urls = re.findall(r'\bhttps?://\S+\.pdf\b', content)
            #INverse: non_pdf_urls = re.findall(r'\bhttps://\S+(?!\.pdf)\b', content)
            return pdf_urls

    def download_and_save_pdf(self, pdf_urls, output_folder):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        for url in pdf_urls:
            # Get the filename from the URL
            filename = url.split('/')[-1]
            # Download the PDF content
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    # Save the PDF content to a file in the output folder
                    with open(os.path.join(output_folder, filename), 'wb') as file:
                        file.write(response.content)
                    print(f"Downloaded: {filename}")
                else:
                    print(f"Failed to download: {filename}")
            except requests.exceptions.ConnectionError as e:
                print(f"ConnectionError: {e}")
                # Handle the connection error gracefully, e.g., log the error, provide a user-friendly message, or take appropriate actions.

            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                # Handle other unexpected errors as needed.


    def downloadPdfs(self, eventTimelineCsv, pdfFileFolder):
        pdf_urls = self.find_pdf_urls(eventTimelineCsv)
        self.download_and_save_pdf(pdf_urls, pdfFileFolder)