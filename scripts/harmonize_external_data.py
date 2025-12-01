import spacy
from spacy.tokens import DocBin
import os
import json

BASE_DIR = "/home/jim/5_NER10_Training_2025-11-24/NER11_Gold_Standard/external_data/standardized"
MAPPING_FILE = "/home/jim/5_NER10_Training_2025-11-24/NER11_Gold_Standard/reference/SCHEMA_MAPPING.json"

def harmonize_dataset(filepath, mapping):
    try:
        nlp = spacy.blank("en")
        doc_bin = DocBin().from_disk(filepath)
        new_doc_bin = DocBin()
        
        docs = list(doc_bin.get_docs(nlp.vocab))
        change_count = 0
        
        for doc in docs:
            new_ents = []
            for ent in doc.ents:
                if ent.label_ in mapping:
                    # Create new span with mapped label
                    new_label = mapping[ent.label_]
                    if new_label != ent.label_:
                        ent.label_ = new_label
                        change_count += 1
                new_ents.append(ent)
            doc.ents = new_ents
            new_doc_bin.add(doc)
            
        # Overwrite file
        new_doc_bin.to_disk(filepath)
        return change_count
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return 0

def main():
    with open(MAPPING_FILE, 'r') as f:
        mapping = json.load(f)
        
    print(f"Loaded {len(mapping)} mappings.")
    
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith(".spacy"):
                filepath = os.path.join(root, file)
                print(f"Harmonizing {file}...")
                changes = harmonize_dataset(filepath, mapping)
                print(f"  -> {changes} entities updated.")

if __name__ == "__main__":
    main()
