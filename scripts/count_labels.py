import spacy
from spacy.tokens import DocBin
import sys
import os
from collections import Counter

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 count_labels.py <path_to_spacy_file>")
        sys.exit(1)

    filepath = sys.argv[1]
    print(f"Analyzing {filepath}...")

    nlp = spacy.blank("en")
    doc_bin = DocBin().from_disk(filepath)
    docs = list(doc_bin.get_docs(nlp.vocab))

    label_counts = Counter()
    total_ents = 0

    for doc in docs:
        for ent in doc.ents:
            label_counts[ent.label_] += 1
            total_ents += 1

    print(f"\nTotal Documents: {len(docs)}")
    print(f"Total Entities: {total_ents}")
    print(f"Unique Labels: {len(label_counts)}")
    print("-" * 40)
    print(f"{'Label':<30} | {'Count':<10}")
    print("-" * 40)
    
    # Sort by count ascending (to find starving labels)
    for label, count in label_counts.most_common()[::-1]:
        print(f"{label:<30} | {count:<10}")

if __name__ == "__main__":
    main()
