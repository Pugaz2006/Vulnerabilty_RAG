import os
import subprocess
import json

root_directory = "." 
results_file = "slither_master_results.json"
master_log = []

print("[*] Starting Slither Batch Analysis...")

for dirpath, dirnames, filenames in os.walk(root_directory):
    for filename in filenames:
        if filename.endswith(".sol"):
            full_path = os.path.join(dirpath, filename)
            print(f"\n[*] Analyzing: {full_path}")
            
            temp_json = "temp_slither_output.json"
            
            # Run Slither and force it to output to a temporary JSON file
            # capture_output=True hides the terminal spam
            subprocess.run(["slither", full_path, "--json", temp_json], capture_output=True)
            
            # If Slither successfully analyzed the file, it will create the temp JSON
            if os.path.exists(temp_json):
                try:
                    with open(temp_json, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        
                    # Navigate Slither's JSON structure to find the bugs
                    detectors = data.get("results", {}).get("detectors", [])
                    has_bugs = len(detectors) > 0
                    
                    master_log.append({
                        "file_tested": full_path,
                        "compiled_successfully": True,
                        "ai_predicted_vulnerable": has_bugs,
                        "bug_count": len(detectors)
                    })
                    print(f"    -> ✅ Compiled! Slither found {len(detectors)} issues.")
                    
                except json.JSONDecodeError:
                    print("    -> ⚠️ Error parsing Slither output.")
                    
                # Delete the temp file so it is clean for the next loop
                os.remove(temp_json)
                
            else:
                # If no JSON was created, Slither failed to compile the contract
                master_log.append({
                    "file_tested": full_path,
                    "compiled_successfully": False,
                    "ai_predicted_vulnerable": None,
                    "error": "Compilation failed"
                })
                print("    -> ❌ Compilation failed (Skipped).")

# Save the final results
with open(results_file, "w", encoding="utf-8") as f:
    json.dump(master_log, f, indent=4)
    
print("\n" + "="*50)
print(f"✅ BATCH COMPLETE! All results saved to '{results_file}'")
print("="*50)