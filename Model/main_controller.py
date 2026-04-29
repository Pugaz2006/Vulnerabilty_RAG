import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
# add ur api key here

# =====================================================================
# 1. Strict Output Schema
# =====================================================================
class JudgeVerdict(BaseModel):
    is_vulnerable: bool = Field(description="True if ANY functional bug exists, False if it is perfectly safe.")
    bug_type: str = Field(description="MUST be 'Known_RAG_Pattern' if it matches database context, otherwise 'Zero_Day_Logic_Flaw', or 'None'.")
    vulnerability_category: str = Field(description="The specific category of the bug (e.g., Price Manipulation). MUST match a RAG category if applicable.")
    reasoning: str = Field(description="Step-by-step proof of the exploit or defense.")

# =====================================================================
# 2. The Multi-Agent Auditor
# =====================================================================
class AgenticAuditor:
    # def __init__(self):
    #     print("[*] Initializing the Highly-Constrained RAG System...")
        
    #     # self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
    #     self.encoder = SentenceTransformer('flax-sentence-embeddings/st-codesearch-distilroberta-base')
    #     self.index = faiss.read_index("smartcontract_memory.faiss")
    #     with open("rag_metadata.json", "r", encoding='utf-8') as f:
    #         self.metadata = json.load(f)
            
    #     self.client = genai.Client()
    #     self.model_name = "gemini-2.5-flash-lite"
    def __init__(self):
        print("[*] Initializing the Highly-Constrained RAG System...")
        
        # --- THE UPGRADE ---
        print("[*] Loading Jina-v2-base-code (8192 Token Window)...")
        self.encoder = SentenceTransformer('jinaai/jina-embeddings-v2-base-code', trust_remote_code=True)
        
        # Load the newly built database
        self.index = faiss.read_index("smartcontract_memory.faiss") 
        with open("rag_metadata.json", "r", encoding='utf-8') as f:
            self.metadata = json.load(f)
            
        self.client = genai.Client()
        self.model_name = "gemini-2.5-flash-lite"

    def retrieve_context(self, target_code: str, k=3): 
        """Fetches the TOP 5 closest matches to prevent retrieval gaps."""
        print(f"[*] Searching FAISS database for Top {k} closest patterns...")
        query_vector = self.encoder.encode(target_code).astype('float32').reshape(1, -1)
        distances, indices = self.index.search(query_vector, k) 
        
        contexts = []
        for idx in indices[0]:
            if idx != -1 and idx < len(self.metadata):
                contexts.append(self.metadata[idx])
        return contexts

    def run_attacker(self, target_code: str, rag_contexts: list) -> str:
        print("[*] Agent A (Attacker) is analyzing based on RAG constraints...")
        
        # Format the top 3 contexts
        context_str = ""
        for i, ctx in enumerate(rag_contexts):
            context_str += f"\n--- RAG MATCH {i+1} ---\nCategory: {ctx['category']}\nCode Snippet:\n{ctx['code_snippet']}\n"

        prompt = f"""
        You are an elite Smart Contract Attacker.
        
        We retrieved these historical exploits from our database:
        {context_str}

        NEW CONTRACT TO AUDIT:
        {target_code}

        EXECUTE A TWO-PRONGED ATTACK:
        Phase 1 (Known Patterns): Look STRICTLY at the RAG Matches above. Does the new contract suffer from ANY of these exact same flaws (e.g., Price Manipulation)? If so, write the exploit and explicitly state which RAG Category it matches.
        Phase 2 (Zero-Day Hunt): ONLY if the RAG Matches do not apply, look for novel business logic flaws.

        Provide your most lethal exploit strategy.
        """
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.4) # Lowered temp so it sticks to the data
        )
        return response.text

    def run_defender(self, target_code: str, attacker_arg: str) -> str:
        print("[*] Agent B (Defender) is challenging the attack logic...")
        prompt = f"""
        You are the Defender. The Attacker has proposed the following exploit:
        
        ATTACKER'S ARGUMENT: 
        {attacker_arg}
        
        NEW CONTRACT:
        {target_code}
        
        TASK:
        Prove the Attacker wrong using strict Solidity security principles. Look for missing modifiers, bounds, or logic that blocks the attack. If the attack is completely valid, you must concede.
        """
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.1)
        )
        return response.text

   
    def run_judge(self, target_code: str, attacker_arg: str, defender_arg: str, rag_contexts: list) -> dict:
        print("[*] Agent C (Judge) is issuing the final verdict...")
        
        valid_categories = [ctx['category'] for ctx in rag_contexts]
        
        prompt = f"""
        You are the Judge. Review the New Contract, Attacker's exploit, and Defender's rebuttal.
        
        New Contract: {target_code}
        Attacker's Case: {attacker_arg}
        Defender's Case: {defender_arg}
        
        CRITICAL CLASSIFICATION RULES:
        1. Evaluate the RAG Categories: {valid_categories}. 
        2. If the Attacker's most lethal and obvious exploit strongly matches one of these RAG categories, set `bug_type` to "Known_RAG_Pattern" and use that category.
        3. SMART OVERRIDE: If the RAG categories are weak matches (e.g., generic math or safe) BUT you clearly see a severe functional bug (e.g., Price Manipulation, Reentrancy, State Inconsistency), you MUST reject the RAG categories.
        4. If you use the Smart Override, set `bug_type` to "Zero_Day_Logic_Flaw" and set `vulnerability_category` to the actual industry-standard name of the bug you found (e.g., "Price Manipulation").
        
        Output your final ruling strictly according to the provided JSON schema.
        """
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=JudgeVerdict,
                temperature=0.0
            )
        )
        
        return json.loads(response.text)

    def execute_audit(self, file_path: str):
        print(f"\n{'='*60}\nSTARTING ALIGNED RAG AUDIT: {file_path}\n{'='*60}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                target_code = f.read()
        except FileNotFoundError:
            print(f"[!] Error: Target file {file_path} not found.")
            return

        # 1. RAG Retrieval (Top 3)
        rag_data_list = self.retrieve_context(target_code, k=3)
        if rag_data_list:
            print(f"    -> Retrieved Top Matches: {[ctx['category'] for ctx in rag_data_list]}")
        else:
            rag_data_list = [{"category": "None", "code_snippet": "None"}]

        # 2. Multi-Agent Debate
        attacker_report = self.run_attacker(target_code, rag_data_list)
        defender_report = self.run_defender(target_code, attacker_report)
        
        # 3. Final JSON Judgment
        final_verdict = self.run_judge(target_code, attacker_report, defender_report, rag_data_list)
        
        print("\n" + "="*60)
        print("FINAL AUDIT REPORT")
        print("="*60)
        print(json.dumps(final_verdict, indent=4))
        return final_verdict

# =====================================================================
# 3. Run the Tool
# =====================================================================
if __name__ == "__main__":
    if not os.environ.get("GEMINI_API_KEY"):
        print("[!] Warning: GEMINI_API_KEY environment variable is not set.")
        
    auditor = AgenticAuditor()
    
    # Run this on your simple price manipulation file!
    test_file = 'test.sol' 
    
    auditor.execute_audit(test_file)
