import configparser

class Config:
    def __init__(self, config_file='config_template.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

        # Access values from the configuration file
        self.nsa_pdf_timeline = self.config.get('Settings', 'NSA_PDF_TIMELINE')
        self.nsa_csv_timeline = self.config.get('Settings', 'NSA_CSV_TIMELINE')
        self.pdfs_folder = self.config.get('Settings', 'PDFS_FOLDER')
        self.jsons_folder = self.config.get('Settings', 'JSONS_FOLDER')
        self.openai_api_key = self.config.get('Settings', 'OPENAI_API_KEY')
        self.chroma_db_persist = self.config.get('Settings', 'CHROMA_DB_PERSIST')

# Create an instance of the Config class
#config_instance = Config()
#print(config_instance.nsa_pdf_timeline)
#print(config_instance.nsa_csv_timeline)