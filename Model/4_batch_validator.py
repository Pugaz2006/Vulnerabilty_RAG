import os
import json
import time
from main_controller import AgenticAuditor

def run_batch_validation(validation_folder):
    print(f"[*] Starting Dual-Metric Batch Validation on folder: {validation_folder}")
    
    if not os.path.exists(validation_folder):
        print(f"[!] Error: Folder '{validation_folder}' not found.")
        return

    auditor = AgenticAuditor()
    
    # ==========================================
    # Metrics Trackers
    # ==========================================
    results = []
    
    # 1. Binary Classification Tracking (Bug vs. No Bug)
    TP = 0  # True Positive
    FP = 0  # False Positive
    TN = 0  # True Negative
    FN = 0  # False Negative
    
    # 2. Categorical Tracking (Specific Bug Type)
    exact_category_matches = 0

    for dirpath, _, filenames in os.walk(validation_folder):
        ground_truth_category = os.path.basename(dirpath)
        if ground_truth_category == os.path.basename(validation_folder):
            continue

        for filename in filenames:
            if filename.endswith(".sol"):
                filepath = os.path.join(dirpath, filename)
                print(f"\n{'='*40}")
                print(f"[*] Auditing: {filename}")
                print(f"[*] Ground Truth Label: '{ground_truth_category}'")
                
                # If the folder is 'safe_contracts', it should NOT have bugs.
                is_actually_vulnerable = (ground_truth_category != "safe_contracts")

                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        target_code = f.read()

                    # Execute the RAG + Multi-Agent Pipeline
                    rag_data = auditor.retrieve_context(target_code)
                    if not rag_data:
                        rag_data = {"category": "None", "code_snippet": "None"}
                        
                    attacker_report = auditor.run_attacker(target_code, rag_data)
                    defender_report = auditor.run_defender(target_code, attacker_report)
                    verdict = auditor.run_judge(target_code, attacker_report, defender_report)

                    ai_says_vulnerable = verdict.get('is_vulnerable', False)
                    ai_predicted_category = verdict.get('vulnerability_category', 'None')
                    category_status = "N/A"

                    # ==========================================
                    # Evaluate Binary & Categorical Results
                    # ==========================================
                    if is_actually_vulnerable and ai_says_vulnerable:
                        TP += 1
                        status = "✅ True Positive (Bug Found)"
                        
                        # Clean strings to compare (e.g., 'time_manipulation' vs 'Time Manipulation')
                        gt_clean = ground_truth_category.lower().replace("_", " ").strip()
                        pred_clean = ai_predicted_category.lower().replace("_", " ").strip()
                        
                        # Check if the predicted category matches the folder name
                        if gt_clean in pred_clean or pred_clean in gt_clean:
                            exact_category_matches += 1
                            category_status = "🎯 Exact Category Match"
                        else:
                            category_status = f"⚠️ Category Mismatch (AI classified as: '{ai_predicted_category}')"

                    elif not is_actually_vulnerable and ai_says_vulnerable:
                        FP += 1
                        status = "❌ False Positive (Hallucination)"
                    elif not is_actually_vulnerable and not ai_says_vulnerable:
                        TN += 1
                        status = "✅ True Negative (Correctly deemed safe)"
                    elif is_actually_vulnerable and not ai_says_vulnerable:
                        FN += 1
                        status = "❌ False Negative (Missed the bug)"

                    print(f"    -> Binary Result: {status}")
                    if is_actually_vulnerable and ai_says_vulnerable:
                        print(f"    -> Category Result: {category_status}")

                    # Log the detailed results for your report
                    results.append({
                        "file": filename,
                        "ground_truth_category": ground_truth_category,
                        "ai_predicted_category": ai_predicted_category,
                        "binary_status": status,
                        "category_status": category_status,
                        "ai_bug_type_flag": verdict.get('bug_type'),
                        "reasoning": verdict.get('reasoning')
                    })

                    # Pause to respect API rate limits
                    time.sleep(4) 

                except Exception as e:
                    print(f"[!] Failed to process {filename}: {e}")

    # ==========================================
    # Final Metric Calculations
    # ==========================================
    total_files = TP + TN + FP + FN
    
    # Binary Metrics
    binary_accuracy = (TP + TN) / max(total_files, 1)
    precision = TP / max((TP + FP), 1)
    recall = TP / max((TP + FN), 1)
    f1_score = 2 * (precision * recall) / max((precision + recall), 1)
    
    # Categorical Metrics
    categorical_match_rate = exact_category_matches / max(TP, 1)

    print("\n" + "="*50)
    print("🏆 FINAL VALIDATION METRICS")
    print("="*50)
    print(f"Total Files Audited: {total_files}")
    print(f"True Positives (TP) : {TP}")
    print(f"False Positives (FP): {FP}")
    print(f"True Negatives (TN) : {TN}")
    print(f"False Negatives (FN): {FN}")
    print("-" * 50)
    print("🔬 1. BINARY CLASSIFICATION (Did it find a bug?)")
    print(f"Accuracy  : {binary_accuracy * 100:.2f}%")
    print(f"Precision : {precision * 100:.2f}%")
    print(f"Recall    : {recall * 100:.2f}%")
    print(f"F1-Score  : {f1_score * 100:.2f}%")
    print("-" * 50)
    print("🎯 2. CATEGORICAL ACCURACY (Did it find the expected bug?)")
    print(f"Exact Matches: {exact_category_matches} out of {TP} True Positives")
    print(f"Match Rate   : {categorical_match_rate * 100:.2f}%")
    print("="*50)

    # Save detailed report
    with open("validation_results_log.json", "w") as f:
        json.dump(results, f, indent=4)
    print("[+] Detailed JSON log saved to 'validation_results_log.json'")

if __name__ == "__main__":
    VALIDATION_FOLDER = "validation_set"
    run_batch_validation(VALIDATION_FOLDER)