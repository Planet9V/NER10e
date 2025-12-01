import json
import time
import os
from datetime import datetime
import sys

# Configuration
MODEL_DIR = "/home/jim/5_NER10_Training_2025-11-24/NER11_Gold_Standard/models/ner11_v2"
META_FILE = os.path.join(MODEL_DIR, "model-last", "meta.json")
CHECK_INTERVAL = 30  # Check every 30 seconds

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_training_status():
    if not os.path.exists(META_FILE):
        return None
    
    try:
        with open(META_FILE, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        return None

def format_duration(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d}"

def main():
    print(f"Starting NER11 Training Monitor...")
    print(f"Watching: {META_FILE}")
    
    last_step = -1
    last_report_time = 0
    start_time = time.time()
    
    while True:
        status = get_training_status()
        
        current_time = time.time()
        elapsed_total = current_time - start_time
        
        if status:
            # Extract metrics
            perf = status.get('performance', {})
            ents_f = perf.get('ents_f', 0.0)
            ents_p = perf.get('ents_p', 0.0)
            ents_r = perf.get('ents_r', 0.0)
            
            # SpaCy meta.json doesn't always store current step directly in a simple field, 
            # but usually it's tracked. However, 'model-last' is saved at specific steps.
            # We can infer progress or just report the current metrics.
            # Actually, spacy's meta.json contains "performance" but maybe not "step".
            # Let's check if we can find the step. 
            # Often it's not explicitly in meta.json for the model, but the metrics are.
            # We will assume that if the file changed, it's a new step (every 200).
            
            # Get file modification time to detect updates
            mtime = os.path.getmtime(META_FILE)
            
            should_report = False
            reason = ""
            
            # Condition 1: New checkpoint (file updated)
            if mtime > last_report_time:
                # It's a new update (approx every 200 steps based on config)
                should_report = True
                reason = "Checkpoint Update"
                last_report_time = mtime
            
            # Condition 2: 15 minutes passed
            # We'll use a separate timer for the 15m interval if no file update happened?
            # Actually, the user wants a report "every 15 minutes AND when each 200 step has been reached".
            # Since the file updates every 200 steps, the file update covers the "200 step" requirement.
            # The "15 minutes" requirement is likely a fallback if training is slow.
            
            if (current_time - last_report_time) > (15 * 60):
                should_report = True
                reason = "15 Minute Interval"
                last_report_time = current_time

            if should_report or last_step == -1:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\n[{timestamp}] REPORT ({reason})")
                print("-" * 50)
                print(f"Duration: {format_duration(elapsed_total)}")
                print(f"F1 Score: {ents_f:.4f}")
                print(f"Precision: {ents_p:.4f}")
                print(f"Recall:    {ents_r:.4f}")
                
                # Try to print per-type scores if available and interesting
                if 'ents_per_type' in perf:
                    print("\nTop 5 Entities (by F1):")
                    sorted_ents = sorted(perf['ents_per_type'].items(), key=lambda x: x[1].get('f', 0), reverse=True)[:5]
                    for label, scores in sorted_ents:
                        print(f"  {label:<20} F1: {scores.get('f', 0):.4f}")
                print("-" * 50)
                
                last_step = 1 # Just mark as initialized
                
        else:
            # Waiting for first checkpoint
            sys.stdout.write(f"\r[{format_duration(elapsed_total)}] Waiting for first checkpoint (step 200)...")
            sys.stdout.flush()
            
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nMonitor stopped.")
