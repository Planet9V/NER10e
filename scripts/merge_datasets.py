import spacy
from spacy.tokens import DocBin
import os
import random
import shutil

# Configuration
# Paths are relative to this script's location to ensure Docker portability
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

CUSTOM_DATA_DIR = "/app/NER11_Gold_Standard/custom_data"
EXTERNAL_DATA_DIR = "/app/NER11_Gold_Standard/external_data/standardized"
OUTPUT_DIR = "/app/NER11_Gold_Standard/final_training_set"

# Capping Strategy (Target ~61,300 Total)
CAP_LIMITS = {
    "CIRCL_vuln": 15000,  # Cap massive dataset at 15k
    # All others default to "All"
}

def load_docs(filepath, limit=None):
    """Loads docs from a .spacy file, optionally with a limit (random sample)."""
    try:
        nlp = spacy.blank("en")
        doc_bin = DocBin().from_disk(filepath)
        docs = list(doc_bin.get_docs(nlp.vocab))
        
        if limit and len(docs) > limit:
            print(f"  - Capping {os.path.basename(filepath)}: {len(docs)} -> {limit}")
            return random.sample(docs, limit)
        
        return docs
    except Exception as e:
        print(f"  - Error loading {filepath}: {e}")
        return []

def main():
    print("=== NER11 Dataset Merge Initiated ===")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    final_train_docs = []
    final_dev_docs = []
    
    # 1. Process Custom Data (Already Weighted 3.0x in conversion step)
    print("\n[1/3] Merging Custom Data...")
    custom_train = load_docs(os.path.join(CUSTOM_DATA_DIR, "train.spacy"))
    custom_dev = load_docs(os.path.join(CUSTOM_DATA_DIR, "dev.spacy"))
    final_train_docs.extend(custom_train)
    final_dev_docs.extend(custom_dev)
    print(f"  - Added {len(custom_train)} Custom Train Docs")
    
    # 2. Process External Data
    print("\n[2/3] Merging External Data...")
    for root, dirs, files in os.walk(EXTERNAL_DATA_DIR):
        for file in files:
            if file.endswith("train.spacy"):
                dataset_name = os.path.basename(root)
                filepath = os.path.join(root, file)
                
                # Determine Limit
                limit = CAP_LIMITS.get(dataset_name, None)
                
                # Load & Add
                print(f"  - Processing {dataset_name}...")
                docs = load_docs(filepath, limit)
                
                # Split External Data 90/10 for Train/Dev (if dev doesn't exist, but here we just merge train to train)
                # Note: External datasets usually have their own dev.spacy, but for simplicity and consistency
                # we often just merge their 'train' into our 'train'. 
                # Let's check if they have a dev set.
                dev_path = os.path.join(root, "dev.spacy")
                if os.path.exists(dev_path):
                    dev_docs = load_docs(dev_path)
                    final_dev_docs.extend(dev_docs)
                else:
                    # If no dev set, split the loaded train docs
                    split_idx = int(len(docs) * 0.9)
                    final_train_docs.extend(docs[:split_idx])
                    final_dev_docs.extend(docs[split_idx:])
                    continue

                final_train_docs.extend(docs)

    # 3. Save Final Datasets
    print("\n[3/3] Saving Final Datasets...")
    
    # Shuffle Training Data
    random.shuffle(final_train_docs)
    
    print(f"  - Final Training Size: {len(final_train_docs)} documents")
    print(f"  - Final Dev Size: {len(final_dev_docs)} documents")
    
    train_db = DocBin(docs=final_train_docs)
    train_db.to_disk(os.path.join(OUTPUT_DIR, "train.spacy"))
    
    dev_db = DocBin(docs=final_dev_docs)
    dev_db.to_disk(os.path.join(OUTPUT_DIR, "dev.spacy"))
    
    print(f"\nSUCCESS: Merged dataset saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
