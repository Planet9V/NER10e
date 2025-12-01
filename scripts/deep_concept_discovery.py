import spacy
import os
import re
from collections import Counter
import multiprocessing
from concurrent.futures import ProcessPoolExecutor

# Configuration
SOURCE_DIR = "/home/jim/5_NER10_Training_2025-11-24/NER11_Gold_Standard/custom_data/source_files"
MASTER_LIST_FILE = "/home/jim/5_NER10_Training_2025-11-24/NER11_Gold_Standard/reference/NER11_ENTITY_MASTER_LIST.md"
REPORT_FILE = "/home/jim/5_NER10_Training_2025-11-24/NER11_Gold_Standard/MISSING_CONCEPTS_REPORT.md"
IGNORE_DIRS = ["Annual_Cyber_Security_Reports"]
MIN_FREQUENCY = 10 # Term must appear at least this many times to be flagged

def load_master_entities():
    """Extracts all entity labels and keywords from the Master List."""
    entities = set()
    with open(MASTER_LIST_FILE, 'r') as f:
        content = f.read()
        # Find all backticked items like `THREAT_ACTOR`
        matches = re.findall(r'`([A-Z0-9_]+)`', content)
        for m in matches:
            entities.add(m)
            # Also add the human readable version as a "known term" to avoid flagging "Threat Actor"
            entities.add(m.replace('_', ' ').lower())
    return entities

def process_file(filepath):
    """Reads a file and extracts potential entity candidates (noun chunks)."""
    try:
        nlp = spacy.load("en_core_web_sm", disable=["ner", "parser"]) # Fast load
        nlp.enable_pipe("senter")
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
            
        doc = nlp(text)
        candidates = []
        
        # Extract Noun Chunks (simple approximation for concepts)
        # Note: en_core_web_sm doesn't have a great noun chunker without parser, 
        # so we'll use a simple regex/tagger approach or just simple token frequency for speed/robustness
        # actually, let's just use simple capitalized phrases for "Proper Noun" candidates
        # and technical looking terms.
        
        # Regex for potential technical terms: Capitalized words or acronyms
        # e.g. "Modbus", "PLC", "Ladder Logic", "ISO 27001"
        matches = re.findall(r'\b[A-Z][a-zA-Z0-9-]+\b(?:\s+[A-Z][a-zA-Z0-9-]+)*', text)
        
        return matches
    except Exception as e:
        return []

def main():
    print("Loading Master Entity List...")
    known_entities = load_master_entities()
    print(f"Loaded {len(known_entities)} known entities/terms.")
    
    files_to_scan = []
    for root, dirs, files in os.walk(SOURCE_DIR):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            if file.endswith(('.md', '.txt')) and not file.startswith('.'):
                files_to_scan.append(os.path.join(root, file))
                
    print(f"Scanning {len(files_to_scan)} files for missing concepts...")
    
    # Parallel Processing
    term_counter = Counter()
    
    # Use a smaller pool to avoid memory issues, though this is text processing so it's lighter
    with ProcessPoolExecutor(max_workers=4) as executor:
        results = executor.map(process_file, files_to_scan)
        
        for file_terms in results:
            term_counter.update(file_terms)
            
    # Filter results
    missing_concepts = []
    print("Analyzing results...")
    
    for term, count in term_counter.most_common(500):
        # Normalize for check
        norm_term = term.replace(' ', '_').upper()
        norm_term_lower = term.lower()
        
        if count < MIN_FREQUENCY:
            break
            
        # Check if it's already in our known list (either as LABEL or human readable)
        if norm_term not in known_entities and norm_term_lower not in known_entities:
            # Filter out common noise (Months, Days, Common words)
            if term.lower() not in ["january", "february", "monday", "table", "figure", "section", "chapter", "page"]:
                missing_concepts.append((term, count))

    # Write Report
    with open(REPORT_FILE, 'w') as f:
        f.write("# Missing Concepts Report\n")
        f.write(f"**Files Scanned**: {len(files_to_scan)}\n")
        f.write(f"**Min Frequency**: {MIN_FREQUENCY}\n\n")
        f.write("The following high-frequency terms appear in the Custom Data but are NOT explicitly defined in the Master Entity List.\n")
        f.write("Please review and indicate which should be added as new Entity Types.\n\n")
        f.write("| Term | Frequency | Suggested Category |\n")
        f.write("| :--- | :--- | :--- |\n")
        for term, count in missing_concepts:
            f.write(f"| **{term}** | {count} | ? |\n")
            
    print(f"Report generated: {REPORT_FILE}")

if __name__ == "__main__":
    multiprocessing.set_start_method('spawn')
    main()
