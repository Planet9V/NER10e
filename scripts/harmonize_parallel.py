import spacy
from spacy.tokens import DocBin
import os
import json
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
import functools

BASE_DIR = "/home/jim/5_NER10_Training_2025-11-24/NER11_Gold_Standard/external_data/standardized"
MAPPING_FILE = "/home/jim/5_NER10_Training_2025-11-24/NER11_Gold_Standard/reference/SCHEMA_MAPPING.json"

def process_dataset(file_info, mapping):
    filepath = file_info
    try:
        nlp = spacy.blank("en")
        doc_bin = DocBin().from_disk(filepath)
        new_doc_bin = DocBin()
        
        # CRITICAL FIX: Use generator, do NOT convert to list()
        # This prevents loading millions of Doc objects into RAM at once
        doc_generator = doc_bin.get_docs(nlp.vocab)
        
        change_count = 0
        doc_count = 0
        
        for doc in doc_generator:
            doc_count += 1
            new_ents = []
            has_changes = False
            for ent in doc.ents:
                if ent.label_ in mapping:
                    new_label = mapping[ent.label_]
                    if new_label != ent.label_:
                        ent.label_ = new_label
                        has_changes = True
                        change_count += 1
                new_ents.append(ent)
            
            if has_changes:
                doc.ents = new_ents
            
            new_doc_bin.add(doc)
            
        # Overwrite file with harmonized data
        new_doc_bin.to_disk(filepath)
        return f"SUCCESS: {os.path.basename(filepath)} - {change_count} entities updated (scanned {doc_count} docs)"
    except Exception as e:
        return f"FAILURE: {os.path.basename(filepath)} - Error: {str(e)}"

def main():
    # Load mapping
    with open(MAPPING_FILE, 'r') as f:
        mapping = json.load(f)
    
    print(f"Taskmaster: Loaded {len(mapping)} schema mappings.")
    
    # Discovery Phase
    files_to_process = []
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith(".spacy"):
                files_to_process.append(os.path.join(root, file))
    
    print(f"Taskmaster: Dispatched {len(files_to_process)} datasets to worker pool.")
    
    # Execution Phase - Parallel Processing
    # Using fewer workers than CPUs to avoid OOM if multiple huge files load at once
    max_workers = min(4, os.cpu_count() or 1) 
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Create a partial function with the mapping fixed
        worker_func = functools.partial(process_dataset, mapping=mapping)
        
        results = list(executor.map(worker_func, files_to_process))
        
    # Reporting Phase
    print("\n=== Taskmaster Report ===")
    for result in results:
        print(result)

if __name__ == "__main__":
    multiprocessing.set_start_method('spawn') # Safer for spacy/torch
    main()
