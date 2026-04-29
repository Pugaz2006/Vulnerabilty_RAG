import json

with open("slither_comparison_results.json", "r") as f:
    data = json.load(f)

TP = sum(1 for d in data if "True Positive" in d["evaluation_result"])
FP = sum(1 for d in data if "False Positive" in d["evaluation_result"])
TN = sum(1 for d in data if "True Negative" in d["evaluation_result"])
FN = sum(1 for d in data if "False Negative" in d["evaluation_result"])

accuracy = (TP + TN) / len(data) if len(data) > 0 else 0
precision = TP / (TP + FP) if (TP + FP) > 0 else 0
recall = TP / (TP + FN) if (TP + FN) > 0 else 0

print(f"SLITHER METRICS -- TP: {TP} | FP: {FP} | TN: {TN} | FN: {FN}")
print(f"Accuracy: {accuracy:.2%} | Precision: {precision:.2%} | Recall: {recall:.2%}")