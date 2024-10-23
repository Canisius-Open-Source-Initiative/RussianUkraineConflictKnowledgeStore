import json
from collections import defaultdict


def evaluate_documents(json_file):
    # Load the JSON file
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Initialize storage for document names
    llm_docs = defaultdict(list)

    # Process each question entry and collect document names per LLM response
    for entry in data:
        llm_docs['openai'].extend(entry.get('openai_source_documents', []))
        llm_docs['minilm'].extend(entry.get('minilm_source_documents', []))
        llm_docs['mpnet'].extend(entry.get('mpnet_source_documents', []))

    # Convert lists to sets for set operations
    openai_docs = set(llm_docs['openai'])
    minilm_docs = set(llm_docs['minilm'])
    mpnet_docs = set(llm_docs['mpnet'])

    # Calculate common and unique documents
    common_all = openai_docs & minilm_docs & mpnet_docs
    common_two_openai_minilm = (openai_docs & minilm_docs) - common_all
    common_two_openai_mpnet = (openai_docs & mpnet_docs) - common_all
    common_two_minilm_mpnet = (minilm_docs & mpnet_docs) - common_all
    unique_openai = openai_docs - common_all - common_two_openai_minilm - common_two_openai_mpnet
    unique_minilm = minilm_docs - common_all - common_two_openai_minilm - common_two_minilm_mpnet
    unique_mpnet = mpnet_docs - common_all - common_two_openai_mpnet - common_two_minilm_mpnet

    # Calculate counts
    num_common_all = len(common_all)
    num_common_two = len(common_two_openai_minilm) + len(common_two_openai_mpnet) + len(common_two_minilm_mpnet)
    num_unique = len(unique_openai) + len(unique_minilm) + len(unique_mpnet)

    # Print results
    print("Documents common to all LLMs ({}):".format(num_common_all))
    print(list(common_all))

    print("\nDocuments common to two LLMs ({}):".format(num_common_two))
    print("OpenAI and MiniLM:")
    print(list(common_two_openai_minilm))
    print("OpenAI and MPNet:")
    print(list(common_two_openai_mpnet))
    print("MiniLM and MPNet:")
    print(list(common_two_minilm_mpnet))

    print("\nDocuments unique to one LLM ({}):".format(num_unique))
    print("Unique to OpenAI:")
    print(list(unique_openai))
    print("Unique to MiniLM:")
    print(list(unique_minilm))
    print("Unique to MPNet:")
    print(list(unique_mpnet))


# Example usage
evaluate_documents('../results.json')
