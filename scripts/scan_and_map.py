import os
import json

SOURCE_DIR = "/home/jim/5_NER10_Training_2025-11-24/NER11_Gold_Standard/custom_data/source_files"
MANIFEST_FILE = "/home/jim/5_NER10_Training_2025-11-24/NER11_Gold_Standard/custom_data_manifest.json"

# Simplified Categories based on user feedback: "ALL DATA IS VALUABLE"
CATEGORIES = {
    "A": {"name": "Gold Standard (Enhanced)", "weight": 3.0}, # The 60+ specific extracts
    "B": {"name": "Standard Training Data", "weight": 1.0},   # EVERYTHING else that is text
    "D": {"name": "Invalid (Non-Text)", "weight": 0.0}        # Images, binaries, empty files
}

def categorize_file(filepath, filename):
    # Category D: Physically unusable files
    if not filename.endswith(('.md', '.txt', '.json', '.csv')):
        return "D"
    if os.path.getsize(filepath) < 10: # Empty
        return "D"

    # Category A: Gold Standard Extracts (Enhanced)
    if "_EXTRACT.md" in filename and "Sector" in filepath:
        return "A"

    # Category B: EVERYTHING ELSE IS VALUABLE
    return "B"

def main():
    manifest = []
    stats = {"A": 0, "B": 0, "D": 0}

    for root, dirs, files in os.walk(SOURCE_DIR):
        for file in files:
            filepath = os.path.join(root, file)
            category = categorize_file(filepath, file)
            
            stats[category] += 1
            manifest.append({
                "filepath": filepath,
                "category": category,
                "weight": CATEGORIES[category]["weight"]
            })

    with open(MANIFEST_FILE, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    main()
