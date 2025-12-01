import spacy
from spacy.tokens import DocBin
import sys
import os

def main():
    train_path = "/app/NER11_Gold_Standard/final_training_set/train.spacy"
    dev_path = "/app/NER11_Gold_Standard/final_training_set/dev.spacy"
    
    print(f"Loading datasets from {train_path} and {dev_path}...")
    nlp = spacy.blank("en")
    
    train_db = DocBin().from_disk(train_path)
    dev_db = DocBin().from_disk(dev_path)
    
    train_docs = list(train_db.get_docs(nlp.vocab))
    dev_docs = list(dev_db.get_docs(nlp.vocab))
    
    print(f"Original Train size: {len(train_docs)}")
    print(f"Original Dev size: {len(dev_docs)}")
    
    # 1. Identify Dev Hashes
    dev_hashes = set()
    for doc in dev_docs:
        dev_hashes.add(doc.text) # Using text as hash for deduplication
        
    # 2. Filter Train Docs (Remove Overlaps)
    clean_train_docs = []
    overlaps = 0
    for doc in train_docs:
        if doc.text in dev_hashes:
            overlaps += 1
        else:
            clean_train_docs.append(doc)
            
    print(f"Removed {overlaps} overlapping documents from Train.")
    
    # 3. Filter Noise Labels (SOFTWARE_VERSION, SEVERITY_LEVEL)
    noise_labels = {"SOFTWARE_VERSION", "SEVERITY_LEVEL"}
    
    def filter_labels(docs):
        cleaned_docs = []
        removed_ents = 0
        for doc in docs:
            new_ents = []
            for ent in doc.ents:
                if ent.label_ in noise_labels:
                    removed_ents += 1
                else:
                    new_ents.append(ent)
            doc.ents = new_ents
            cleaned_docs.append(doc)
        return cleaned_docs, removed_ents

    clean_train_docs, train_removed = filter_labels(clean_train_docs)
    clean_dev_docs, dev_removed = filter_labels(dev_docs)
    
    print(f"Removed {train_removed} noise entities from Train.")
    print(f"Removed {dev_removed} noise entities from Dev.")
    
    # 4. Save Cleaned Datasets
    print("Saving cleaned datasets...")
    train_out = DocBin(docs=clean_train_docs)
    train_out.to_disk(train_path)
    
    dev_out = DocBin(docs=clean_dev_docs)
    dev_out.to_disk(dev_path)
    
    print(f"Final Train size: {len(clean_train_docs)}")
    print(f"Final Dev size: {len(clean_dev_docs)}")
    print("SUCCESS: Dataset cleaned.")

if __name__ == "__main__":
    main()
