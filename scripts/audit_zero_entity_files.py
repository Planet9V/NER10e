import spacy
from spacy.pipeline import EntityRuler
import os
import re
import json
from collections import defaultdict

# Configuration
SOURCE_DIR = "/app/NER11_Gold_Standard/custom_data/source_files"
MASTER_LIST_FILE = "/app/NER11_Gold_Standard/reference/NER11_ENTITY_MASTER_LIST.md"
IGNORE_DIRS = ["Annual_Cyber_Security_Reports"] # These are huge PDFs usually, maybe skip or check?

def load_master_entities():
    """Parses the Master List to build a dictionary of Label -> [Terms]."""
    entity_map = {}
    current_label = None
    
    with open(MASTER_LIST_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith("### "):
                current_label = line.replace("### ", "").strip()
            elif current_label and "`" in line:
                terms = re.findall(r'`([^`]+)`', line)
                for term in terms:
                    if current_label not in entity_map:
                        entity_map[current_label] = []
                    entity_map[current_label].append(term)
                    # Add human readable version
                    human_term = term.replace('_', ' ')
                    if human_term != term:
                         entity_map[current_label].append(human_term)
    return entity_map

def create_nlp(entity_map):
    nlp = spacy.blank("en")
    ruler = nlp.add_pipe("entity_ruler")
    patterns = []
    for label, terms in entity_map.items():
        for term in terms:
            patterns.append({"label": label, "pattern": term})
            if " " in term:
                 token_pattern = [{"LOWER": t.lower()} for t in term.split()]
                 patterns.append({"label": label, "pattern": token_pattern})
            else:
                 patterns.append({"label": label, "pattern": [{"LOWER": term.lower()}]})
    ruler.add_patterns(patterns)
    nlp.max_length = 2000000 # Increase limit
    return nlp

def main():
    print("Loading Master List...")
    entity_map = load_master_entities()
    nlp = create_nlp(entity_map)
    
    print(f"Scanning {SOURCE_DIR}...")
    
    total_files = 0
    zero_entity_files = []
    files_by_dir = defaultdict(list)
    
    for root, dirs, files in os.walk(SOURCE_DIR):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            if not file.endswith(('.md', '.txt')):
                continue
                
            filepath = os.path.join(root, file)
            
            # Skip huge files
            if os.path.getsize(filepath) > 1500000:
                print(f"Skipping {file} (Too large)")
                continue

            total_files += 1
            
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
                
                if not text.strip():
                    continue # Empty file
                    
                doc = nlp(text)
                
                if len(doc.ents) == 0:
                    rel_path = os.path.relpath(filepath, SOURCE_DIR)
                    zero_entity_files.append(rel_path)
                    dirname = os.path.dirname(rel_path)
                    files_by_dir[dirname].append(os.path.basename(filepath))
                    
            except Exception as e:
                print(f"Error processing {file}: {e}")

    print(f"\n--- AUDIT RESULTS ---")
    print(f"Total Files Scanned: {total_files}")
    print(f"Files with ZERO Entities: {len(zero_entity_files)} ({len(zero_entity_files)/total_files*100:.1f}%)")
    
    print("\n--- ZERO ENTITY FILES BY DIRECTORY ---")
    for dirname, files in sorted(files_by_dir.items()):
        print(f"\nDirectory: {dirname} ({len(files)} files)")
        # Print first 5 files as examples
        for f in files[:5]:
            print(f"  - {f}")
        if len(files) > 5:
            print(f"  ... and {len(files)-5} more")

    # Save full report
    with open("DATA_COVERAGE_AUDIT.md", "w") as f:
        f.write("# Data Coverage Audit Report\n\n")
        f.write(f"**Total Files**: {total_files}\n")
        f.write(f"**Zero Entity Files**: {len(zero_entity_files)}\n\n")
        f.write("## Directories with Unused Data\n")
        for dirname, files in sorted(files_by_dir.items()):
            f.write(f"\n### {dirname}\n")
            for fname in files:
                f.write(f"- {fname}\n")
                
    print("\nFull report saved to DATA_COVERAGE_AUDIT.md")

if __name__ == "__main__":
    main()
