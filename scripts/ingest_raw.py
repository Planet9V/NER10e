import os
import json
from pathlib import Path
from tqdm import tqdm

# Configuration
DATA_ROOT = "/home/jim/5_NER10_Training_2025-11-24/Training_Data_Check_to_see"
OUTPUT_FILE = "/home/jim/5_NER10_Training_2025-11-24/ner10_pipeline/corpus/raw_data.jsonl"

def main():
    files = list(Path(DATA_ROOT).rglob("*"))
    data = []
    
    print(f"Scanning {len(files)} files for raw ingestion...")
    
    for file_path in tqdm(files):
        if file_path.is_dir():
            continue
            
        # Filter extensions
        if file_path.suffix.lower() not in ['.md', '.txt']:
            continue
            
        try:
            text = file_path.read_text(errors='ignore')
            
            # Skip empty or very short files
            if len(text.strip()) < 50:
                continue
                
            # Skip files that are already heavily tagged (handled by ingest_tags.py)
            # Heuristic: if > 5 tags, skip
            if text.count("[[") > 5 or text.count("<COGNITIVE_BIAS>") > 5:
                continue
            
            # Create Prodigy Task
            task = {
                "text": text,
                "meta": {
                    "source": str(file_path.name),
                    "path": str(file_path)
                }
            }
            data.append(task)
            
        except Exception as e:
            # print(f"Skipping {file_path}: {e}")
            pass
            
    # Save to JSONL
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        for entry in data:
            f.write(json.dumps(entry) + "\n")
            
    print(f"Ingested {len(data)} raw files to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
