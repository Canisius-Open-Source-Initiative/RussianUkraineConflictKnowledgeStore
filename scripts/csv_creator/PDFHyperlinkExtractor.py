import pdfminer
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdftypes import resolve1

# This script extracts hyperlinks for a PDF and the
# associated text.

class PDFHyperlinkExtractor:
    # Function to check if two rectangles intersect
    def rect_intersect(self, rect1, rect2):
      x1, y1, x2, y2 = rect1
      X1, Y1, X2, Y2 = rect2

      # Check if rectangles intersect
      if (x1 <= X1 and x2 >= X1) or (X1 <= x1 and X2 >= x1):
        if (y1 <= Y1 and y2 >= Y1) or (Y1 <= y1 and Y2 >= y1):
          return True

      return False

    def extract_hyperlinks_from_pdf(self, pdf_path):
        # Initialize a counter to limit the number of hyperlinks to extract
        counter = 0
        # Initialize a list to store extracted hyperlinks
        hyperlinks = []

        # Open the PDF file in binary read mode
        with open(pdf_path, 'rb') as file:
            # Create a PDF parser and document objects
            parser = PDFParser(file)
            document = PDFDocument(parser)

            # Iterate through pages in the PDF
            for page in PDFPage.create_pages(document):
                # Get annotations for the current page
                annotations = page.annots
                if annotations:
                    for annotation in annotations:
                        # Resolve annotation references
                        if isinstance(annotation, pdfminer.pdfparser.PDFObjRef):
                            annotation = resolve1(annotation)
                        if isinstance(annotation, dict):
                            # Check if the annotation is a hyperlink
                            subtype = annotation.get('Subtype')
                            if subtype and subtype.name == 'Link':
                                # Extract URI (link) from the annotation
                                uri = annotation.get('A').get('URI')
                                if uri:
                                    # Get the rectangle coordinates of the hyperlink
                                    hyperlink_rect = annotation.get('Rect')
                                    # Create PDFMiner resources
                                    manager = PDFResourceManager()
                                    laparams = LAParams()
                                    device = PDFPageAggregator(manager, laparams=laparams)
                                    interpreter = PDFPageInterpreter(manager, device)

                                    # Process the current page for text layout
                                    interpreter.process_page(page)

                                    # Get the layout result
                                    page_layout = device.get_result()

                                    # Initialize a holder for link text
                                    holder = 'holder'
                                    for element in page_layout:
                                        if isinstance(element, LTTextBox):
                                            text_rect = element.bbox
                                            # Check if text and hyperlink rectangles intersect
                                            if self.rect_intersect(text_rect, hyperlink_rect):
                                                holder = element.get_text().strip()
                                    # Extract link text or use URI if no link text is available
                                    link_text = annotation.get('A').get('S')
                                    link_text = link_text if link_text else uri
                                    # Append the extracted hyperlink to the list
                                    hyperlinks.append({'uri': uri.decode(), 'text': holder})
                                    counter = counter + 1


        # Return the list of extracted hyperlinks
        return hyperlinks

