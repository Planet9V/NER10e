import spacy
from spacy.tokens import DocBin
import os
import json

BASE_DIR = "/home/jim/5_NER10_Training_2025-11-24/NER11_Gold_Standard/external_data/standardized"

def get_labels_from_spacy(filepath):
    try:
        nlp = spacy.blank("en")
        doc_bin = DocBin().from_disk(filepath)
        labels = set()
        # Sample first 100 docs to be fast
        docs = list(doc_bin.get_docs(nlp.vocab))[:100]
        for doc in docs:
            for ent in doc.ents:
                labels.add(ent.label_)
        return list(labels)
    except Exception as e:
        return [f"Error: {str(e)}"]

def main():
    report = {}
    
    # Walk through standardized directory
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith("train.spacy"):
                dataset_name = os.path.basename(root)
                filepath = os.path.join(root, file)
                print(f"Scanning {dataset_name}...")
                labels = get_labels_from_spacy(filepath)
                report[dataset_name] = sorted(labels)

    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
