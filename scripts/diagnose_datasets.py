import spacy
from spacy.tokens import DocBin
import os

BASE_DIR = "/home/jim/5_NER10_Training_2025-11-24/NER11_Gold_Standard/external_data/standardized"

# Labels that SHOULD be gone if harmonization worked
OLD_LABELS = ["SQL_INJECTION", "PLATFORM", "SOFTWARE_PRODUCT", "MITIGATION_KEYWORD"]

def check_file(filepath):
    try:
        nlp = spacy.blank("en")
        doc_bin = DocBin().from_disk(filepath)
        
        # Check first few docs for old labels
        docs = list(doc_bin.get_docs(nlp.vocab))[:50]
        found_old = []
        for doc in docs:
            for ent in doc.ents:
                if ent.label_ in OLD_LABELS:
                    found_old.append(ent.label_)
        
        if found_old:
            return f"VALID (But NOT Harmonized): {os.path.basename(filepath)} - Found old labels: {set(found_old)}"
        else:
            return f"VALID (Harmonized): {os.path.basename(filepath)}"
            
    except Exception as e:
        return f"CORRUPTED: {filepath} - {str(e)}"

def main():
    print("Scanning for corrupted files and checking harmonization status...")
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith(".spacy"):
                filepath = os.path.join(root, file)
                result = check_file(filepath)
                if "CORRUPTED" in result or "NOT Harmonized" in result:
                    print(result)

if __name__ == "__main__":
    main()
