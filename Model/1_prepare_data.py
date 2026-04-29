import os
import json
import re

def split_into_functions(solidity_code):
    """Splits Solidity code into individual function chunks."""
    # This regex looks for 'function name(...)' patterns
    functions = re.split(r'(?=\bfunction\b)', solidity_code)
    # Clean up and filter out chunks that are too small (like interfaces)
    return [f.strip() for f in functions if len(f.strip()) > 50]

def convert_nested_folders_to_jsonl(root_folder, output_filename):
    print(f"[*] Scanning root directory: {root_folder}...")
    
    if not os.path.exists(root_folder):
        print(f"[!] Error: The folder '{root_folder}' does not exist.")
        return

    valid_chunks = 0
    file_count = 0
    
    with open(output_filename, 'w', encoding='utf-8') as jsonl_file:
        for dirpath, dirnames, filenames in os.walk(root_folder):
            current_category = os.path.basename(dirpath)
            
            # Skip the root folder itself
            if current_category == os.path.basename(root_folder):
                continue
                
            for filename in filenames:
                if filename.endswith(".sol"):
                    filepath = os.path.join(dirpath, filename)
                    file_count += 1
                    
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            full_code = f.read().strip()
                            
                        if not full_code:
                            continue

                        # --- NEW: CHUNKING LOGIC ---
                        chunks = split_into_functions(full_code)
                        
                        # If no functions found (e.g. just a state variable file), use the whole file
                        if not chunks:
                            chunks = [full_code]

                        for i, chunk in enumerate(chunks):
                            data_obj = {
                                "id": f"{file_count}_{i}", # Unique ID for each function
                                "category": current_category,
                                "filename": filename,
                                "description": f"Function chunk {i} from {filename} (Type: {current_category})",
                                "code_snippet": chunk
                            }
                            jsonl_file.write(json.dumps(data_obj) + '\n')
                            valid_chunks += 1
                        
                    except Exception as e:
                        print(f"[!] Error reading {filepath}: {e}")
                        
    print(f"\n[+] Success! Processed {file_count} files into {valid_chunks} functional chunks.")
    print(f"[+] Output saved to: {output_filename}")

if __name__ == "__main__":
    ROOT_DATASET_FOLDER = "dataset" 
    OUTPUT_FILE = "smartcontract_dataset.jsonl"
    convert_nested_folders_to_jsonl(ROOT_DATASET_FOLDER, OUTPUT_FILE)