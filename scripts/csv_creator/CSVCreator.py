import re
from io import StringIO

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage


class CSVCreator:

    event_start_formats = [
        r'\d{4}-\d{4}',           # Example: 2010-2020
        r'\d{4} –[A-Za-z]+ \d{4}', # Example: 2018 –late 2022
        r'Mid-\d{4}',             # Example: Mid-2019
        r'Early \d{4}',           # Example: Early 2021
        r'\d{4}',                 # Example: 2014
        r'\d{4} on',              # Example: 2014 on
        r'Winter \d{4}',          # Example: Winter 2018
        r'Summer \d{4}',          # Example: Summer 2022
        r'[A-Za-z]+ \d{1,2}, \d{4}', # Example: July 11, 2014

        #r'[A-Za-z]+ \d{1,2} –[A-Za-z]+ \d{1,2}, \d{4}', # Example: February 23 –April 8, 2022
        r'[A-Za-z]+ \d{4} – [A-Za-z]+ \d{4}',  # Example: January 2021 – October 2021
        #r'[A-Za-z]+ \d{1,2},? \d{4} – [A-Za-z]+ \d{1,2},? \d{4}'  # Example: February 2021 – July 2022
        r'Late [A-Za-z]+ \d{4}',  # Example: Late December 2021
        r'Mid-[A-Za-z]+ \d{4}',   # Example: Mid-June 2022
        r'End [A-Za-z]+ \d{4}',    # Example: End April 2022
        r'[A-Za-z]+ \d{1,2} & [A-Za-z]+ \d{1,2}, \d{4}',  # Example: July 27 & August 3, 2019
        #r'[A-Za-z]+ \d{1,2},? \d{4}'  # Example: February 2021
        r'[A-Za-z]+ \d{4}',  # Example: August 2020
        r'[A-Za-z]+-[A-Za-z]+ \d{4}',  # Example: November-December 2021
        r'[A-Za-z]+ \d{1,2}-\d{1,2},? \d{4}',  # Example: October 4-17, 2018
        #todo
        # January–February 2022
        # February – Early May, 2022
        # February 23 – April 8, 2022
        # Pre-February 24, 2022
    ]

    def extract_text_from_pdf_miner(self, pdf_path):
        # Create a PDF resource manager to manage resources
        resource_manager = PDFResourceManager()

        # Create a StringIO object to store the extracted text
        return_string = StringIO()

        # Set the character encoding for the extracted text (UTF-8)
        codec = 'utf-8'

        # Set the layout parameters for PDF parsing
        laparams = LAParams()

        # Use a context manager (with statement) for resource management
        converter = TextConverter(resource_manager, return_string, laparams=laparams)

        # Open the PDF file in binary read mode
        with open(pdf_path, 'rb') as file:
            # Create a PDF interpreter to process the pages
            interpreter = PDFPageInterpreter(resource_manager, converter)

            # Iterate through each page in the PDF
            for page in PDFPage.get_pages(file):
                # Process the current page and extract text
                interpreter.process_page(page)

        # Get the extracted text from the StringIO object
        extracted_text = return_string.getvalue()

        # Return the extracted text as a string
        return extracted_text

    def split_monthly_sections(self, text):
        lines = text.split('\n')
        events = []
        current_event = []

        # Process the document line by line
        date = ''
        oldDate = ''
        for line in lines:
            # Check if the line matches any of the date formats
            matched = False
            for pattern in self.event_start_formats:
                match = re.match(pattern, line)
                if match:
                    matched = True
                    oldDate = date
                    date = match.group(0)
            if matched:
                # If it matches, create a new archived event
                if current_event:
                    result = "".join(current_event)
                    # Try to remove some invalid date collection entries.
                    if len(result) > 15:
                        events.append({'date': oldDate, 'text':result , 'urls': set()})
                current_event = []
                current_event = [line]  # Start a new event
            else:
                # If it doesn't match, add the line to the current event
                if current_event:
                    current_event.append(line + "\n")

        # Append the last event to the list of events
        #if current_event:
        #    events.append(current_event)

        return events

    def add_url_pointers_to_sections(self, monthly_sections, extracted_hyperlinks):
        for section in monthly_sections:
            found = False
            for link in extracted_hyperlinks:
                if len(link['text'].strip()) != 0 and link['text'] in section['text']:
                    section['urls'].add(link['uri'])
                    found = True

