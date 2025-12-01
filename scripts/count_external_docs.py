import spacy
from spacy.tokens import DocBin
import os
import json

BASE_DIR = "/home/jim/5_NER10_Training_2025-11-24/NER11_Gold_Standard/external_data/standardized"

def count_docs(filepath):
    try:
        nlp = spacy.blank("en")
        doc_bin = DocBin().from_disk(filepath)
        # DocBin doesn't have a length, need to iterate (fast enough for headers)
        return len(doc_bin)
    except Exception as e:
        return -1

def main():
    stats = {}
    total = 0
    
    print("Counting documents in external datasets...")
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith("train.spacy"):
                filepath = os.path.join(root, file)
                dataset_name = os.path.basename(root)
                count = count_docs(filepath)
                stats[dataset_name] = count
                if count > 0:
                    total += count

    print(json.dumps(stats, indent=2))
    print(f"Total External Documents: {total}")

if __name__ == "__main__":
    main()
