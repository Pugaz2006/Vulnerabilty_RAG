import pandas as pd
import os
import re

# --- CONFIGURATION ---
INPUT_CSV = 'LabeledDataset.csv'
OUTPUT_FOLDER = 'dataset'  # This will be the main folder name

def get_vulnerability_folder(code):
    """
    Analyzes the code content to find the <report> tag and returns a clean folder name.
    """
    # 1. Search for the <report> tag (e.g., <yes> <report> BAD_RANDOMNESS)
    match = re.search(r'<report>\s*([A-Za-z0-9_\.\s]+)', code)
    
    if match:
        tag = match.group(1).strip()
        # Clean and Normalize the tag into a folder name
        if "BAD_RANDOMNESS" in tag: return "Bad_Randomness"
        if "TOD" in tag: return "Front_Running_TOD"
        if "REENTRANCY" in tag: return "Reentrancy"
        if "Gasless" in tag: return "Gasless_Send"
        if "UNCHECKED" in tag: return "Unchecked_Low_Level_Call"
        if "ARITHMETIC" in tag: return "Arithmetic_Overflow"
        if "delegatecall" in tag.lower(): return "Unsafe_Delegatecall"
        if "tx.origin" in tag or "tx_origin" in tag: return "Tx_Origin_Phishing"
        if "TIME" in tag: return "Time_Manipulation"
        if "suicide" in tag.lower(): return "Unsafe_SelfDestruct"
        if "ACCESS" in tag: return "Access_Control"
    
    # 2. Check for explicit "Safe" contracts (vulnerable lines = 0)
    if "@vulnerable_at_lines: 0" in code:
        return "Safe_No_Vulnerability"
        
    return "Uncategorized"

def main():
    # 1. Load the CSV
    print(f"Reading {INPUT_CSV}...")
    try:
        df = pd.read_csv(INPUT_CSV)
    except FileNotFoundError:
        print(f"Error: Could not find {INPUT_CSV}. Make sure it is in this folder.")
        return

    # 2. Create the main dataset folder
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
        print(f"Created folder: {OUTPUT_FOLDER}/")

    # 3. Iterate through each row and save the file
    count = 0
    for index, row in df.iterrows():
        filename = row['nameid']
        content = row['content']
        
        # Determine the sub-folder name
        folder_name = get_vulnerability_folder(content)
        
        # Create the sub-folder (e.g., dataset/Reentrancy/)
        full_folder_path = os.path.join(OUTPUT_FOLDER, folder_name)
        if not os.path.exists(full_folder_path):
            os.makedirs(full_folder_path)
        
        # Save the .sol file
        file_path = os.path.join(full_folder_path, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        count += 1

    print(f"\nSuccess! Extracted {count} files.")
    print(f"Check the '{OUTPUT_FOLDER}' folder to see your sorted dataset.")

if __name__ == "__main__":
    main()