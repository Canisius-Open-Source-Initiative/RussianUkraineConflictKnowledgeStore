# Usage example
# The target PDF is found here: https://nsarchive.gwu.edu/document/29562-cyber-vault-ukraine-timeline
import csv
import re

from scripts.Config import Config
from scripts.csv_creator.CSVCreator import CSVCreator
from scripts.csv_creator.PDFHyperlinkExtractor import PDFHyperlinkExtractor
from scripts.file_downloader.PdfDownloader import  PdfDownloader
from scripts.file_downloader.HtmlDownloader import  HtmlDownloader
from scripts.knowledge_store_examples.TextAsContext import  TextAsContext
from scripts.knowledge_store_examples.VectorStoreAsContextUnPersisted import  VectorStoreAsContextUnPersisted
from scripts.knowledge_store_examples.VectorStoreAsContextPersisted import VectorStoreAsContextPersisted
from scripts.analytics.DomainCounts import DomainCounts
from scripts.analytics.DomainEndings import DomainEndings

config_instance = Config("config_local.ini")
csv_creator = CSVCreator()
pdfHyperlinkExtractor = PDFHyperlinkExtractor()
pdfDownloader = PdfDownloader()
htmlDownloader = HtmlDownloader()
textAsContext = TextAsContext()
vectorStoreAsContextUnPersisted = VectorStoreAsContextUnPersisted()
vectorStoreAsContextPersisted = VectorStoreAsContextPersisted()
domainCounts = DomainCounts()
domainEndings = DomainEndings()

def createCSV():
    print("1. Extract hyperlinks from PDF files")
    extracted_hyperlinks = pdfHyperlinkExtractor.extract_hyperlinks_from_pdf(config_instance.nsa_pdf_timeline)

    print("2. Extract text from PDF")
    extracted_text = csv_creator.extract_text_from_pdf_miner(config_instance.nsa_pdf_timeline)
    monthly_sections = csv_creator.split_monthly_sections(extracted_text)

    print("3. Create CSV")
    csv_creator.add_url_pointers_to_sections(monthly_sections, extracted_hyperlinks)
    pattern = r'[^\x09\x0A\x0D\x20-\x7E]+|\x0C|^\s*$|^\d+\s*$'
    with open(config_instance.nsa_csv_timeline, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['date', 'text', 'urls'])
        writer.writeheader()
        for item in monthly_sections:
            text = item['text']
            cleaned_text = re.sub(pattern, '', text, flags=re.MULTILINE)
            item['text'] = cleaned_text
            writer.writerow(item)
    print("4. Create URL Listing")
    with open(config_instance.nsa_urls, 'w') as txtfile:
        txtfile.write("Harvested URLs")
        for item in monthly_sections:
            urls = item['urls']
            for url in urls:
                txtfile.write(url+'\n')

def downloadPdfs():
    print("Downloading PDFs")
    pdfDownloader.downloadPdfs(config_instance.nsa_csv_timeline,config_instance.pdfs_folder)

def downloadHtmlPages():
    print("Downloading Html Pages")
    htmlDownloader.downloadHtmlsAsTextFiles(config_instance.nsa_csv_timeline, config_instance.jsons_folder)
def performURLAnalytics():
    #domainCounts.main(config_instance.nsa_urls)
    domainEndings.main(config_instance.nsa_urls)

#1. Create the csv
#createCSV()
#performURLAnalytics()

#2. Download PDFs
#downloadPdfs()

#3. Download HTML Pages
#downloadHtmlPages()

#4. Run Text As Context only knowledge search
#textAsContext.demo(config_instance.nsa_csv_timeline, config_instance.openai_api_key)

#5. Run vector store but unpersisted knowledge search
#vectorStoreAsContextUnPersisted.demo(config_instance.nsa_csv_timeline, config_instance.openai_api_key)

#6. Run vector store with persisted knowledge search using OpenAI
vectorStoreAsContextPersisted.demo(config_instance)
