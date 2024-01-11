from langchain.document_loaders import CSVLoader
import json
import chardet

def loadNSAUkraineEventsCSV(csv_file_path):
    # Load sample documents into memory
    loader = CSVLoader(
        file_path=csv_file_path,
        csv_args={
            "delimiter": ",",
            "quotechar": '"',
            "fieldnames": ["date", "text", "urls"],
        },
    )

    documents = loader.load()
    return documents

def loadNSAUkraineEventsCSVAsJSON(json_file_path):
    encoding = detect_file_encoding(json_file_path)
    print(json_file_path)
    print(f'The file is encoded in: {encoding}')
    try:
        with open(json_file_path) as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        print("File not found!")
    except json.decoder.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")

def loadNSAUkraineEventsCSVAsJSON(json_file_path):
    encoding = detect_file_encoding(json_file_path)
    print(json_file_path)
    print(f'The file is encoded in: {encoding}')
    try:
        with open(json_file_path) as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        print("File not found!")
    except json.decoder.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")

def detect_file_encoding(file_path):
    with open(file_path, 'rb') as file:
        rawdata = file.read()
        result = chardet.detect(rawdata)
    return result['encoding']

