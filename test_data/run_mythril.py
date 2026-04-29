import os
import subprocess
import json
import sys

# 1. Dynamically hunt down where Python installed myth.exe
scripts_dir = os.path.join(os.path.dirname(sys.executable), "Scripts")
myth_exe = os.path.join(scripts_dir, "myth.exe")

# Point directly to the set1 folder
target_folder = "./set1"
results_file = "mythril_set1_results.json"
master_log = []

print(f"[*] Found Mythril at: {myth_exe}")
print("[*] Starting Mythril Batch Analysis on Set 1...")

# os.walk digs into every sub-folder inside set1
for dirpath, dirnames, filenames in os.walk(target_folder):
    for filename in filenames:
        if filename.endswith(".sol"):
            full_path = os.path.join(dirpath, filename)
            print(f"\n[*] Interrogating: {full_path}")
            
            # 2. Use the EXACT path to myth.exe inside the command
            command = f'"{myth_exe}" analyze "{full_path}" --execution-timeout 60 -o json'
            
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                shell=True
            )
            
            try:
                # Parse Mythril's JSON output
                data = json.loads(result.stdout)
                issues = data.get("issues", [])
                has_bugs = len(issues) > 0
                
                master_log.append({
                    "file_tested": full_path,
                    "ai_predicted_vulnerable": has_bugs,
                    "bug_count": len(issues),
                    "status": "Completed"
                })
                print(f"    -> ✅ Done! Mythril found {len(issues)} issues.")
                
            except json.JSONDecodeError:
                # If it fails to output JSON, it means it timed out or crashed
                master_log.append({
                    "file_tested": full_path,
                    "ai_predicted_vulnerable": None,
                    "bug_count": 0,
                    "status": "Failed / Timed Out"
                })
                print("    -> ⚠️ Mythril Timed Out or Failed to Compile!")

# Save the final results
with open(results_file, "w", encoding="utf-8") as f:
    json.dump(master_log, f, indent=4)
    
print(f"\n✅ MYTHRIL BATCH COMPLETE! Saved to {results_file}")