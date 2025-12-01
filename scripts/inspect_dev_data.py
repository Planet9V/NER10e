import spacy
from spacy.tokens import DocBin
from collections import Counter
import sys

def inspect_data(path):
    print(f"--- Inspecting: {path} ---")
    try:
        doc_bin = DocBin().from_disk(path)
        docs = list(doc_bin.get_docs(spacy.blank("en").vocab))
        
        print(f"Total Documents: {len(docs)}")
        
        entity_count = 0
        label_counts = Counter()
        docs_with_ents = 0
        
        for doc in docs:
            ents = doc.ents
            if ents:
                docs_with_ents += 1
                entity_count += len(ents)
                for ent in ents:
                    label_counts[ent.label_] += 1
        
        print(f"Total Entities: {entity_count}")
        print(f"Documents with Entities: {docs_with_ents} ({docs_with_ents/len(docs)*100:.1f}%)")
        
        if entity_count == 0:
            print("\n[CRITICAL WARNING] No entities found in this dataset!")
        else:
            print("\nTop 20 Labels:")
            for label, count in label_counts.most_common(20):
                print(f"  {label}: {count}")
                
    except Exception as e:
        print(f"Error reading file: {e}")

if __name__ == "__main__":
    inspect_data("/app/NER11_Gold_Standard/final_training_set/dev.spacy")
