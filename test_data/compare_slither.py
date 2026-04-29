import os
import json
import shutil

slither_log = "slither_master_results.json"
truth_file = "refined_analysis_truths.json"
output_folder = "benchmark_compilable"
comparison_log = "slither_comparison_results.json"

os.makedirs(output_folder, exist_ok=True)

print("[*] Parsing Ground Truth Data...")
# Fix the smashed JSON format
with open(truth_file, "r", encoding="utf-8") as f:
    raw_text = f.read()
fixed_json_text = "[" + raw_text.replace("}{", "},{") + "]"
truth_data = json.loads(fixed_json_text)

# Build a dictionary mapping just the filename to its true status
truth_map = {}
for dataset in truth_data:
    contracts = dataset.get("contract", [])
    bugs = dataset.get("bugs", [])
    
    for i in range(len(contracts)):
        filename = os.path.basename(contracts[i])
        # If the bug string is empty, the contract is safe. Otherwise, it's vulnerable.
        is_vulnerable = (bugs[i] != "")
        truth_map[filename] = is_vulnerable

print("[*] Loading Slither Results...")
with open(slither_log, "r", encoding="utf-8") as f:
    slither_data = json.load(f)

final_results = []
copied_count = 0
missing_count = 0  # Track files that are in the log but deleted from the PC

for entry in slither_data:
    if entry.get("compiled_successfully") == True:
        original_path = entry["file_tested"]
        filename = os.path.basename(original_path)
        
        # --- THE FIX: Check if the file physically exists before copying ---
        if not os.path.exists(original_path):
            print(f"⚠️ Skipping missing file: {original_path}")
            missing_count += 1
            continue
        
        # 1. Determine Ground Truth from our map (default to False if missing)
        ground_truth_vulnerable = truth_map.get(filename, False)
        
        # 2. Get Slither's Prediction
        slither_predicted = entry["ai_predicted_vulnerable"]
        
        # 3. Calculate the Metric (FP, TP, FN, TN)
        if slither_predicted == True and ground_truth_vulnerable == True:
            metric = "True Positive (Caught the bug)"
        elif slither_predicted == True and ground_truth_vulnerable == False:
            metric = "False Positive (Cried Wolf - Safe but flagged)"
        elif slither_predicted == False and ground_truth_vulnerable == True:
            metric = "False Negative (Missed the bug)"
        elif slither_predicted == False and ground_truth_vulnerable == False:
            metric = "True Negative (Correctly identified as safe)"
        else:
            metric = "Unknown"

        final_results.append({
            "file": filename,
            "ground_truth_vulnerable": ground_truth_vulnerable,
            "slither_predicted_vulnerable": slither_predicted,
            "evaluation_result": metric,
            "slither_bugs_found": entry.get("bug_count", 0)
        })
        
        # 4. Copy the file for RAG/SmartInv
        destination = os.path.join(output_folder, filename)
        if os.path.exists(destination):
            destination = os.path.join(output_folder, f"{copied_count}_{filename}")
            
        shutil.copy(original_path, destination)
        copied_count += 1

with open(comparison_log, "w", encoding="utf-8") as f:
    json.dump(final_results, f, indent=4)

print("\n" + "="*50)
print(f"✅ Extracted {copied_count} compilable files into '{output_folder}'")
print(f"⚠️ Skipped {missing_count} files that were in the log but not found on your desktop.")
print(f"✅ Saved deep comparison to '{comparison_log}'")
print("="*50)