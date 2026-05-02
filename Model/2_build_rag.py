import json
import faiss
import numpy as np
import os
from sentence_transformers import SentenceTransformer

class VectorMemoryBuilder:
    def __init__(self):
        # print("[*] Loading local ML embedding model (st-codesearch-distilroberta-base)...")
        # This  a highly efficient, open-source model that runs locally.
        # It converts text into a 384-dimensional mathematical vector.
        # self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        # This model is specifically trained on source code and programming languages!
        # self.encoder = SentenceTransformer('flax-sentence-embeddings/st-codesearch-distilroberta-base')
        print("[*] Loading High-Capacity Jina-v2 Code Model...")
        # encoder = SentenceTransformer('jinaai/jina-embeddings-v2-base-code', trust_remote_code=True)
        self.encoder = SentenceTransformer('jinaai/jina-embeddings-v2-base-code', trust_remote_code=True)
        self.dimension = self.encoder.get_sentence_embedding_dimension()
        
        # Initialize the FAISS index (Facebook AI Similarity Search)
        # This acts as our ultra-fast vector database.p
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []

    def build_database(self, dataset_path):
        if not os.path.exists(dataset_path):
            print(f"[!] Error: '{dataset_path}' not found. Did you run 1_prepare_data.py?")
            return

        print(f"[*] Reading dataset: {dataset_path}")
        
        vectors = []
        with open(dataset_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    code = data.get('code_snippet', '')
                    category = data.get('category', 'Unknown')
                    filename = data.get('filename', 'Unknown')
                    
                    if not code: continue
                    
                    # We combine the category and the code. This ensures the ML model
                    # captures BOTH the structural logic and the domain context.
                    combined_text = f"Vulnerability Category: {category}. Code: {code}"
                    
                    # Convert the text into a numerical array (embedding)
                    embedding = self.encoder.encode(combined_text)
                    vectors.append(embedding)
                    
                    # Save the human-readable metadata so we can retrieve it later
                    self.metadata.append({
                        "id": data.get('id'),
                        "category": category,
                        "filename": filename,
                        "code_snippet": code
                    })
                    
                except Exception as e:
                    print(f"[!] Error parsing JSON line: {e}")
                    continue
                    
        if vectors:
            # FAISS requires the vectors to be in a specific numpy float32 format
            print(f"[*] Vectorizing {len(vectors)} contracts... This might take a few seconds.")
            vector_matrix = np.array(vectors).astype('float32')
            
            # Add all vectors to the database
            self.index.add(vector_matrix)
            print(f"\n[+] Successfully indexed {self.index.ntotal} smart contracts into the database.")
            
            # Save the database and metadata to your hard drive
            faiss.write_index(self.index, "smartcontract_memory.faiss")
            with open("rag_metadata.json", "w", encoding='utf-8') as m_file:
                json.dump(self.metadata, m_file, indent=4)
                
            print("[+] RAG Database saved as 'smartcontract_memory.faiss'")
            print("[+] Metadata saved as 'rag_metadata.json'")
        else:
            print("[!] No valid data found to index.")

if __name__ == "__main__":
    DATASET_FILE = "smartcontract_dataset.jsonl"
    builder = VectorMemoryBuilder()
    builder.build_database(DATASET_FILE)