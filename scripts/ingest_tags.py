import os
import re
import json
import spacy
from spacy.tokens import DocBin
from pathlib import Path
from neo4j import GraphDatabase
from tqdm import tqdm

# Configuration
DATA_ROOT = "/home/jim/5_NER10_Training_2025-11-24/Training_Data_Check_to_see"
OUTPUT_DIR = "/home/jim/5_NER10_Training_2025-11-24/ner10_pipeline/corpus"
MAPPING_FILE = "/home/jim/5_NER10_Training_2025-11-24/ner10_pipeline/schema_mapping.json"
NEO4J_URI = "bolt://127.0.0.1:7687"
NEO4J_AUTH = ("neo4j", "neo4j@openspg")

# Regex Patterns
XML_TAG_PATTERN = re.compile(r'<([A-Z_]+)>([^<]+)</\1>')
WIKI_TAG_PATTERN = re.compile(r'\[\[([A-Z_]+):([^\]]+)\]\]')

def load_mapping():
    with open(MAPPING_FILE, 'r') as f:
        return json.load(f)

def get_ner_label(raw_label, mapping):
    """Maps a raw tag (e.g., 'WaterDevice') to a NER label (e.g., 'EQUIPMENT')."""
    # 1. Direct match in keys (e.g., if tag is already EQUIPMENT)
    if raw_label in mapping["entities"]:
        return raw_label
    
    # 2. Value match (e.g., if tag is WaterDevice, find key EQUIPMENT)
    for ner_label, neo4j_labels in mapping["entities"].items():
        if raw_label in neo4j_labels:
            return ner_label
            
    # 3. Fallback: Return None (ignore unknown tags) or keep raw? 
    # Strategy: Log warning and skip to ensure high quality
    return None

def parse_file(file_path, nlp, mapping):
    text = file_path.read_text(errors='ignore')
    
    # We need to strip tags to get the raw text for the Doc, 
    # but keep track of where the entities were.
    # This is tricky with regex because removing tags shifts indices.
    # Strategy: Create a list of (start, end, label, text_content) 
    # and then reconstruct the clean text.
    
    # Actually, simpler: Use regex to find iterators, build a list of entities, 
    # then replace tags in the text with just the content, tracking the offset shift.
    
    clean_text = text
    entities = []
    
    # Process Wiki Tags first [[TYPE:VALUE]]
    # We iterate and replace one by one to handle offsets correctly? 
    # No, better to build a new string and map spans.
    
    # Let's try a robust approach: 
    # 1. Find all matches with their span in original text.
    # 2. Sort by start position.
    # 3. Build new string, appending non-tag text and tag-content.
    # 4. Record new span indices for the tag-content.
    
    matches = []
    
    for m in WIKI_TAG_PATTERN.finditer(text):
        matches.append({
            "start": m.start(),
            "end": m.end(),
            "label": m.group(1),
            "content": m.group(2),
            "type": "wiki"
        })
        
    for m in XML_TAG_PATTERN.finditer(text):
        matches.append({
            "start": m.start(),
            "end": m.end(),
            "label": m.group(1),
            "content": m.group(2),
            "type": "xml"
        })
        
    # Sort matches by start position
    matches.sort(key=lambda x: x["start"])
    
    # Filter overlaps (simple greedy: if overlap, skip)
    filtered_matches = []
    last_end = 0
    for m in matches:
        if m["start"] >= last_end:
            filtered_matches.append(m)
            last_end = m["end"]
            
    # Build clean text and spans
    final_text = ""
    current_idx = 0
    spans = []
    
    for m in filtered_matches:
        # Append text before tag
        final_text += text[current_idx:m["start"]]
        
        # Calculate new start
        entity_start = len(final_text)
        
        # Clean content (trim whitespace)
        raw_content = m["content"]
        clean_content = raw_content.strip()
        
        # Append entity content
        final_text += clean_content
        
        # Calculate new end
        entity_end = len(final_text)
        
        # Map label
        ner_label = get_ner_label(m["label"], mapping)
        if ner_label and len(clean_content) > 0:
            spans.append((entity_start, entity_end, ner_label))
            
        current_idx = m["end"]
        
    # Append remaining text
    final_text += text[current_idx:]
    
    # Create Doc
    doc = nlp.make_doc(final_text)
    ent_spans = []
    for start, end, label in spans:
        span = doc.char_span(start, end, label=label, alignment_mode="contract")
        if span:
            ent_spans.append(span)
        else:
            # Alignment error (tokenization mismatch), skip
            pass
            
    # Filter overlaps in spaCy spans (longest preference)
    doc.ents = spacy.util.filter_spans(ent_spans)
    
    return doc

def main():
    nlp = spacy.blank("en")
    mapping = load_mapping()
    
    train_db = DocBin()
    dev_db = DocBin()
    
    files = list(Path(DATA_ROOT).rglob("*.md"))
    print(f"Scanning {len(files)} files...")
    
    count = 0
    for i, file_path in enumerate(tqdm(files)):
        try:
            # Check if file has tags (quick check)
            content = file_path.read_text(errors='ignore')
            if "[[" not in content and "<" not in content:
                continue
                
            doc = parse_file(file_path, nlp, mapping)
            
            if len(doc.ents) > 0:
                # 80/20 Split
                if i % 5 == 0:
                    dev_db.add(doc)
                else:
                    train_db.add(doc)
                count += 1
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    train_db.to_disk(f"{OUTPUT_DIR}/train.spacy")
    dev_db.to_disk(f"{OUTPUT_DIR}/dev.spacy")
    
    print(f"Processed {count} files with annotations.")
    print(f"Saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
