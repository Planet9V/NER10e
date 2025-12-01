import spacy
from spacy.tokens import DocBin
import os
from tqdm import tqdm

# Configuration
BASE_DIR = "/app/NER11_Gold_Standard"
TRAIN_PATH = os.path.join(BASE_DIR, "final_training_set/train.spacy")
DEV_PATH = os.path.join(BASE_DIR, "final_training_set/dev.spacy")
WINDOW_SIZE = 64
STRIDE = 32

def slice_docs(doc_bin, nlp):
    """Slices docs into overlapping chunks."""
    new_docs = []
    original_docs = list(doc_bin.get_docs(nlp.vocab))
    
    print(f"Processing {len(original_docs)} documents...")
    
    for doc in tqdm(original_docs):
        # Filter Monster Tokens (Research-Based Safety)
        if any(len(token.text) > 100 for token in doc):
            continue

        if len(doc) <= WINDOW_SIZE:
            new_docs.append(doc)
        else:
            # Slice with stride
            start = 0
            while start < len(doc):
                end = start + WINDOW_SIZE
                span = doc[start:end]
                
                # Create a new Doc from the span
                # We use as_doc() to preserve entities and context
                chunk_doc = span.as_doc()
                new_docs.append(chunk_doc)
                
                if end >= len(doc):
                    break
                    
                start += STRIDE
                
    return new_docs

def main():
    print("Initializing Slicing Script...")
    nlp = spacy.blank("en")
    
    # Process Train
    if os.path.exists(TRAIN_PATH):
        print(f"Loading Train: {TRAIN_PATH}")
        train_db = DocBin().from_disk(TRAIN_PATH)
        sliced_train = slice_docs(train_db, nlp)
        print(f"Sliced Train: {len(sliced_train)} docs")
        
        # Save
        train_out = DocBin(docs=sliced_train)
        train_out.to_disk(os.path.join(BASE_DIR, "final_training_set/train_sliced.spacy"))
        print("Saved Train.")
    else:
        print(f"ERROR: Train file not found at {TRAIN_PATH}")

    # Process Dev
    if os.path.exists(DEV_PATH):
        print(f"Loading Dev: {DEV_PATH}")
        dev_db = DocBin().from_disk(DEV_PATH)
        sliced_dev = slice_docs(dev_db, nlp)
        print(f"Sliced Dev: {len(sliced_dev)} docs")
        
        # Save
        dev_out = DocBin(docs=sliced_dev)
        dev_out.to_disk(os.path.join(BASE_DIR, "final_training_set/dev_sliced.spacy"))
        print("Saved Dev.")
    else:
        print(f"ERROR: Dev file not found at {DEV_PATH}")

if __name__ == "__main__":
    main()
