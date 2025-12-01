import spacy
from spacy.pipeline import EntityRuler
from spacy.tokens import DocBin
import os
import re
import random
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
import functools

# Configuration
# Configuration
SOURCE_DIR = "/app/NER11_Gold_Standard/custom_data/source_files"
OUTPUT_DIR = "/app/NER11_Gold_Standard/custom_data"
MASTER_LIST_FILE = "/app/NER11_Gold_Standard/reference/NER11_ENTITY_MASTER_LIST.md"
IGNORE_DIRS = ["Annual_Cyber_Security_Reports"]

def load_master_entities():
    """Parses the Master List to build a dictionary of Label -> [Terms]."""
    entity_map = {}
    current_label = None
    
    with open(MASTER_LIST_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            # Detect Label (e.g., ### THREAT_ACTOR)
            if line.startswith("### "):
                current_label = line.replace("### ", "").strip()
            # Detect Terms (e.g., `APT28`, `Lazarus`)
            elif current_label and "`" in line:
                terms = re.findall(r'`([^`]+)`', line)
                for term in terms:
                    # Add exact term
                    if current_label not in entity_map:
                        entity_map[current_label] = []
                    entity_map[current_label].append(term)
                    
                    # Add human readable version (replace _ with space)
                    human_term = term.replace('_', ' ')
                    if human_term != term:
                         entity_map[current_label].append(human_term)
    
    print(f"DEBUG: Loaded Keys: {list(entity_map.keys())}")
    return entity_map

def create_nlp_with_ruler(entity_map):
    """Creates a blank spaCy model with a populated EntityRuler."""
    nlp = spacy.blank("en")
    ruler = nlp.add_pipe("entity_ruler")
    
    patterns = []
    for label, terms in entity_map.items():
        for term in terms:
            patterns.append({"label": label, "pattern": term})
            # Add case-insensitive version for some robustness
            patterns.append({"label": label, "pattern": [{"LOWER": term.lower()}]})
            
    ruler.add_patterns(patterns)
    return nlp

def process_file(filepath, entity_map_serialized):
    """Worker function to process a single file."""
    try:
        # Re-hydrate NLP in worker (cannot pickle NLP object easily)
        # Optimization: In a real heavy production, we'd initialize this once per worker using 'initializer'
        # But for this scale, re-creating the ruler (fast) or passing patterns is okay.
        # Actually, passing the map and rebuilding is safer.
        nlp = spacy.blank("en")
        ruler = nlp.add_pipe("entity_ruler")
        patterns = []
        for label, terms in entity_map_serialized.items():
            for term in terms:
                 patterns.append({"label": label, "pattern": term})
                 # Simple case insensitive pattern
                 if " " in term:
                     # Multi-word token pattern
                     token_pattern = [{"LOWER": t.lower()} for t in term.split()]
                     patterns.append({"label": label, "pattern": token_pattern})
                 else:
                     patterns.append({"label": label, "pattern": [{"LOWER": term.lower()}]})
        ruler.add_patterns(patterns)

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
            
        doc = nlp(text)
        
        # Determine Weight
        filename = os.path.basename(filepath)
        weight = 1
        if "_EXTRACT.md" in filename:
            weight = 3 # Gold Standard
            
        docs_to_return = []
        if len(doc.ents) > 0:
            # Only keep useful docs
            doc_bytes = doc.to_bytes()
            for _ in range(weight):
                docs_to_return.append(doc_bytes)
                
        return docs_to_return
        
    except Exception as e:
        return []

def main():
    print("Loading Master Entity List...")
    entity_map = load_master_entities()
    print(f"Loaded {len(entity_map)} entity categories.")
    
    files_to_process = []
    for root, dirs, files in os.walk(SOURCE_DIR):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for file in files:
            if file.endswith(('.md', '.txt')):
                files_to_process.append(os.path.join(root, file))
                
    print(f"Dispatched {len(files_to_process)} files to conversion agents...")
    
    train_docs = DocBin()
    dev_docs = DocBin()
    
    # Parallel Execution
    with ProcessPoolExecutor(max_workers=4) as executor:
        # Use partial to pass the entity map
        worker = functools.partial(process_file, entity_map_serialized=entity_map)
        
        results = list(executor.map(worker, files_to_process))
        
    print("Aggregating results...")
    total_docs = 0
    for doc_list in results:
        for doc_bytes in doc_list:
            # Deserialize
            nlp = spacy.blank("en")
            doc = spacy.tokens.Doc(nlp.vocab).from_bytes(doc_bytes)
            
            # Split 80/20
            if random.random() < 0.2:
                dev_docs.add(doc)
            else:
                train_docs.add(doc)
            total_docs += 1
            
    print(f"Total Documents Generated: {total_docs}")
    
    train_docs.to_disk(os.path.join(OUTPUT_DIR, "train.spacy"))
    dev_docs.to_disk(os.path.join(OUTPUT_DIR, "dev.spacy"))
    print(f"Saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    multiprocessing.set_start_method('spawn')
    main()
