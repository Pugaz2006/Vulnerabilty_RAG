import json
import os

# --- CONFIGURATION ---
truth_file = "refined_analysis_truths.json"

# Add or remove files here depending on what you have finished running
evaluation_logs = {
    "Slither": "slither_comparison_results.json",
    "SmartInv": "smartinv_evaluation_results.json",
    # "Multi-Agent RAG": "rag_evaluation_results.json"  <-- Uncomment when ready!
}

# 1. Parse the Ground Truth to get specific bug strings
print("[*] Parsing Ground Truth Data...")
try:
    with open(truth_file, "r", encoding="utf-8") as f:
        raw_text = f.read()
    fixed_json_text = "[" + raw_text.replace("}{", "},{") + "]"
    truth_data = json.loads(fixed_json_text)
except Exception as e:
    print(f"[!] Error loading {truth_file}: {e}")
    exit()

bug_map = {}
for dataset in truth_data:
    contracts = dataset.get("contract", [])
    bugs = dataset.get("bugs", [])
    for i in range(len(contracts)):
        filename = os.path.basename(contracts[i])
        bug_map[filename] = bugs[i].lower()

# 2. Define our categories based on keywords
def categorize_bug(bug_string):
    if not bug_string or bug_string.strip() == "":
        return "Safe"
        
    functional_keywords = ["price manipulation", "business logic", "cross bridge"]
    implementation_keywords = ["privilege escalation", "inconsistent state", "atomicity", "reentrancy"]
    
    is_func = any(kw in bug_string for kw in functional_keywords)
    is_impl = any(kw in bug_string for kw in implementation_keywords)
    
    if is_func and is_impl:
        return "Hybrid"
    elif is_func:
        return "Functional"
    elif is_impl:
        return "Implementation"
    else:
        return "Other/Unknown"

# 3. Analyze each Evaluation Log
for tool_name, log_file in evaluation_logs.items():
    if not os.path.exists(log_file):
        print(f"\n[!] Skipping {tool_name} - Log file '{log_file}' not found.")
        continue

    with open(log_file, "r", encoding="utf-8") as f:
        eval_data = json.load(f)

    # Track totals in the dataset
    totals = {"Functional": 0, "Implementation": 0, "Hybrid": 0, "Safe": 0, "Other/Unknown": 0}
    # Track what the tool actually caught (True Positives)
    caught = {"Functional": 0, "Implementation": 0, "Hybrid": 0, "Other/Unknown": 0}

    for entry in eval_data:
        # Handle slightly different key names depending on the script that generated it
        filename = entry.get("file", entry.get("file_tested", ""))
        filename = filename.split("_", 1)[-1] if "_" in filename and filename.split("_")[0].isdigit() else filename
        
        # Get the evaluation metric (TP, FP, etc.)
        metric = entry.get("evaluation_result", entry.get("status", ""))
        
        # Look up the bug string and categorize it
        bug_string = bug_map.get(filename, "")
        category = categorize_bug(bug_string)
        
        # Increment total count for this category
        totals[category] += 1
        
        # If the tool successfully caught it (True Positive), increment the caught count
        if "True Positive" in metric:
            caught[category] += 1

    # 4. Print the Report for this Tool
    print("\n" + "="*50)
    print(f"📊 {tool_name.upper()} : CATEGORY BREAKDOWN")
    print("="*50)
    
    # We only print the vulnerable categories, not the Safe ones for this part
    for cat in ["Functional", "Implementation", "Hybrid"]:
        total_in_dataset = totals[cat]
        caught_by_tool = caught[cat]
        
        if total_in_dataset > 0:
            percentage = (caught_by_tool / total_in_dataset) * 100
            print(f"🔹 {cat.ljust(15)} : Caught {caught_by_tool} out of {total_in_dataset} ({percentage:.1f}%)")
        else:
            print(f"🔹 {cat.ljust(15)} : 0 in dataset.")
    print("="*50)