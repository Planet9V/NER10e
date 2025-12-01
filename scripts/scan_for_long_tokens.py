import spacy
from spacy.tokens import DocBin
from tqdm import tqdm
import os

BASE_DIR = "/app/NER11_Gold_Standard"
TRAIN_PATH = os.path.join(BASE_DIR, "final_training_set/train.spacy")

def main():
    print("Scanning for Monster Tokens...")
    nlp = spacy.blank("en")
    
    if not os.path.exists(TRAIN_PATH):
        print(f"File not found: {TRAIN_PATH}")
        return

    doc_bin = DocBin().from_disk(TRAIN_PATH)
    docs = list(doc_bin.get_docs(nlp.vocab))
    
    max_char_len = 0
    monster_tokens = []
    
    print(f"Scanning {len(docs)} docs...")
    for i, doc in enumerate(tqdm(docs)):
        for token in doc:
            l = len(token.text)
            if l > max_char_len:
                max_char_len = l
            
            if l > 100:
                monster_tokens.append((i, token.text[:50] + "...", l))

    print(f"Max Token Character Length: {max_char_len}")
    print(f"Found {len(monster_tokens)} tokens > 100 chars.")
    if monster_tokens:
        print("Examples:")
        for idx, text, l in monster_tokens[:10]:
            print(f"Doc {idx}: Len={l} Text={text}")

if __name__ == "__main__":
    main()
