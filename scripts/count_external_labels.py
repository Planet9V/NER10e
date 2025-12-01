import spacy
from spacy.tokens import DocBin
import os
import json
from collections import Counter

BASE_DIR = "/home/jim/5_NER10_Training_2025-11-24/NER11_Gold_Standard/external_data/standardized"

def count_labels(filepath):
    try:
        nlp = spacy.blank("en")
        doc_bin = DocBin().from_disk(filepath)
        c = Counter()
        # Sample first 5000 docs for speed/memory safety
        docs = list(doc_bin.get_docs(nlp.vocab))[:5000]
        for doc in docs:
            for ent in doc.ents:
                c[ent.label_] += 1
        return c
    except Exception as e:
        return Counter()

def main():
    total_counts = Counter()
    dataset_stats = {}

    print("Counting labels in harmonized external datasets...")
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith(".spacy"):
                filepath = os.path.join(root, file)
                dataset_name = os.path.basename(root)
                counts = count_labels(filepath)
                total_counts.update(counts)
                
                if dataset_name not in dataset_stats:
                    dataset_stats[dataset_name] = Counter()
                dataset_stats[dataset_name].update(counts)

    print("\n--- Total External Label Counts ---")
    for label, count in total_counts.most_common():
        print(f"{label}: {count}")

if __name__ == "__main__":
    main()
