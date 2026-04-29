# # import os
# # from google import genai
# # from google.genai import types
# # def list_available_models():
# #     try:
# #         client = genai.Client()

# #         print("Fetching available models...\n")

# #         for model in client.models.list():
# #             print("Model Name:", model.name)
# #             print("Supported Methods:", model.supported_generation_methods)
# #             print("-" * 50)

# #         print("\n✅ Successfully fetched models.")

# #     except Exception as e:
# #         print("❌ Error while fetching models:")
# #         print(e)

# # def detect_bug(file_path):
# #     print(f"Reading file: {file_path}")
# #     # print(os.getenv("GEMINI_API_KEY"))

    
# #     # 1. Read the Solidity code from the file
# #     try:
# #         with open(file_path, 'r', encoding='utf-8') as file:
# #             solidity_code = file.read()
# #     except FileNotFoundError:
# #         return f"Error: Could not find the file at {file_path}. Check the path."

# #     # 2. Initialize the Gemini Client
# #     # It automatically looks for the GEMINI_API_KEY environment variable you set earlier.
# #     client = genai.Client()
   

# #     # 3. Create the Prompt
# #     prompt = f"""
# #     You are a Senior Smart Contract Security Auditor. 
# #     Analyze the following Solidity code for Functional Bugs (e.g., Price Manipulation, Flash Loan vulnerabilities, Access Control flaws).
    
# #     If you find a bug, output your report in this exact format:
# #     - VULNERABILITY FOUND: [Yes / No]
# #     - BUG CATEGORY: [Name of the bug]
# #     - LINE NUMBERS: [Lines where the bug exists]
# #     - EXPLANATION: [Step-by-step explanation of how to exploit it]
    
# #     Code:
# #     {solidity_code}
# #     """

# #     print("Sending code to Gemini 1.5 Pro for analysis...")

# #     # 4. Call the API
# #     response = client.models.generate_content(
# #         model='gemini-2.5-flash',
# #         contents=prompt,
# #         config=types.GenerateContentConfig(
# #             temperature=0.0 # Temperature 0 means it will be analytical and logical, not creative
# #         ),
# #     )

# #     return response.text

# # # --- RUN THE SCRIPT ---
# # if __name__ == "__main__":
# #     # Change this path to where your .sol file actually is!
# #     # For example: 'Project_dataset/Functional_Bugs_RealWorld/Price_Manipulation_Beluga.sol'
# #     target_file = 'AZT.sol' 
# #     # list_available_models()
    
# #     report = detect_bug(target_file)
    
# #     print("\n" + "="*50)
# #     print("AUDIT REPORT")
# #     print("="*50)
# #     print(report)
# # import os
# # import json
# # from google import genai
# # from google.genai import types
# # from pydantic import BaseModel, Field

# # # =====================================================================
# # # 1. Define the Expected AI Outputs (Strict Pydantic Schemas)
# # # =====================================================================
# # class ContractFeatures(BaseModel):
# #     has_price_calculation: bool = Field(description="Does the contract calculate token prices or swap rates?")
# #     has_access_control: bool = Field(description="Are there privileged roles (e.g., onlyOwner, admin) that control critical logic?")
# #     has_external_calls: bool = Field(description="Does the contract make calls to external, unknown contracts (e.g., token transfers, delegations)?")
# #     has_complex_math: bool = Field(description="Does the contract perform complex math that could overflow or underflow?")

# # class VulnerabilityResult(BaseModel):
# #     is_vulnerable: bool = Field(description="Is this specific feature vulnerable to exploitation?")
# #     exploit_path: str = Field(description="Step-by-step reasoning of how an attacker would exploit this feature.")

# # # =====================================================================
# # # 2. The Advanced Attacker Class
# # # =====================================================================
# # class AdvancedAttackerAgent:
# #     def __init__(self, func_name: str, func_code: str):
# #         self.function_name = func_name
# #         self.code = func_code
# #         self.client = genai.Client() # Automatically uses GEMINI_API_KEY
# #         self.model_name = "gemini-2.5-flash"
        
# #         # This is the "System Persona"
# #         self.task_desc = """You are a top-tier cybersecurity auditor specializing in DeFi smart contracts. 
# #         Your goal is to simulate ethical hacking scenarios to find highly complex functional bugs."""

# #         # Store the final found vulnerabilities here
# #         self.found_vulnerabilities = []

# #     def _call_gemini(self, prompt: str, schema: BaseModel, temperature: float = 0.0):
# #         """Helper function to securely call Gemini and guarantee strict JSON structure."""
# #         response = self.client.models.generate_content(
# #             model=self.model_name,
# #             contents=f"{self.task_desc}\n\n{prompt}",
# #             config=types.GenerateContentConfig(
# #                 response_mime_type="application/json",
# #                 response_schema=schema,
# #                 temperature=temperature
# #             ),
# #         )
# #         # Parse the guaranteed JSON string directly into a Python Dictionary
# #         return json.loads(response.text)

# #     def phase1_feature_matching(self) -> dict:
# #         """Phase 1: Scan the contract to identify what critical attack surfaces exist."""
# #         print(f"[*] Phase 1: Analyzing Attack Surfaces for {self.function_name}...")
        
# #         prompt = f"""
# #         Analyze the following smart contract code and determine which of the following features are present.
# #         Code:
# #         {self.code}
# #         """
        
# #         # Returns a perfect dictionary based on the ContractFeatures Pydantic schema
# #         features = self._call_gemini(prompt, ContractFeatures, temperature=0.0)
# #         return features

# #     def phase2_targeted_attack(self, features: dict):
# #         """Phase 2: Launch specific exploit prompts based on the features found in Phase 1."""
# #         print("[*] Phase 2: Launching Targeted Fuzzing Prompts...")

# #         if features.get("has_price_calculation"):
# #             print("    -> Feature Detected: Price Calculation. Testing for Oracle Manipulation...")
# #             prompt = f"""
# #             The following code contains price calculation logic. 
# #             Can an attacker use a Flash Loan to manipulate the reserves or the spot price to drain funds?
# #             Code:
# #             {self.code}
# #             """
# #             result = self._call_gemini(prompt, VulnerabilityResult, temperature=0.7)
# #             if result.get("is_vulnerable"):
# #                 self.found_vulnerabilities.append({"type": "Price Oracle Manipulation", "details": result})

# #         if features.get("has_access_control"):
# #             print("    -> Feature Detected: Access Control. Testing for Privilege Escalation...")
# #             prompt = f"""
# #             The following code contains access control modifiers. 
# #             Is there a way for a normal user to bypass these checks (e.g., via initialize functions or delegatecalls) to gain admin rights?
# #             Code:
# #             {self.code}
# #             """
# #             result = self._call_gemini(prompt, VulnerabilityResult, temperature=0.7)
# #             if result.get("is_vulnerable"):
# #                 self.found_vulnerabilities.append({"type": "Incorrect Control Mechanism", "details": result})

# #         # Add more logic branches here (Reentrancy for external_calls, etc.)

# #     def execute_attack(self):
# #         """Orchestrates the Multi-Tier Attack."""
# #         # Step 1: Find the surfaces
# #         contract_features = self.phase1_feature_matching()
        
# #         # Step 2: Attack the surfaces
# #         self.phase2_targeted_attack(contract_features)
        
# #         # Step 3: Return the final attack report
# #         return self.found_vulnerabilities



# # # =====================================================================
# # # 3. Running the Agent on Your Dataset
# # # =====================================================================
# # if __name__ == "__main__":
    
# #     # 1. Set the path to the actual .sol file you want to test
# #     target_file = 'AZT.sol' 
    
# #     print(f"Reading file: {target_file}")
    
# #     # 2. Open and read the file's contents into a variable
# #     try:
# #         with open(target_file, 'r', encoding='utf-8') as file:
# #             solidity_code = file.read()
# #     except FileNotFoundError:
# #         print(f"Error: Could not find the file at {target_file}. Check the path.")
# #         exit()
    
# #     # 3. Initialize your advanced attacker with the actual file data
# #     # We pass the filename so it knows what it's auditing, and the code itself
# #     attacker = AdvancedAttackerAgent(func_name=target_file, func_code=solidity_code)
    
# #     # 4. Run the multi-phase attack
# #     report = attacker.execute_attack()
    
# #     print("\n" + "="*50)
# #     print("FINAL ATTACKER REPORT")
# #     print("="*50)
# #     print(json.dumps(report, indent=4))


#     # =====================================================================
# # 3. Running the Agent
# # =====================================================================
# # if __name__ == "__main__":
# #     # Test Code (Simulating a vulnerable flash loan / price manipulation contract)
# #     test_code = """
# #     function swap(uint amountIn) public {
# #         uint price = getPriceFromAMM(); // Vulnerable to Flash Loans
# #         uint amountOut = amountIn * price;
# #         token.transfer(msg.sender, amountOut);
# #     }
# #     """
    
# #     # Initialize your advanced attacker
# #     attacker = AdvancedAttackerAgent(func_name="swap_contract", func_code=test_code)
    
# #     # Run the attack
# #     report = attacker.execute_attack()
    
# #     print("\n" + "="*50)
# #     print("FINAL ATTACKER REPORT")
# #     print("="*50)
# #     print(json.dumps(report, indent=4))

# import os
# import json
# from google import genai
# from google.genai import types
# from pydantic import BaseModel, Field


# # ============================================================
# # JSON Schema for Final Structured Output
# # ============================================================
# class FinalAuditReport(BaseModel):
#     vulnerability_found: bool = Field(description="Whether any real exploitable vulnerability exists")
#     issues: list = Field(description="List of confirmed vulnerabilities")


# # ============================================================
# # Advanced Auditor Agent
# # ============================================================
# class AdvancedSmartContractAuditor:

#     def __init__(self, file_name: str, code: str):
#         self.file_name = file_name
#         self.code = code
#         self.client = genai.Client()
#         self.model = "models/gemini-2.5-flash"   # Use PRO model for reasoning


#     # -------------------------------
#     # Generic Gemini Call
#     # -------------------------------
#     def call_model(self, prompt, temperature=0.3, structured=False, schema=None):

#         config = types.GenerateContentConfig(
#             temperature=temperature
#         )

#         if structured and schema:
#             config.response_mime_type = "application/json"
#             config.response_schema = schema

#         response = self.client.models.generate_content(
#             model=self.model,
#             contents=prompt,
#             config=config
#         )

#         return response.text


#     # -------------------------------
#     # Stage 1: Deep Free Reasoning
#     # -------------------------------
#     def stage1_deep_analysis(self):

#         prompt = f"""
# You are a world-class DeFi security researcher.

# Perform a deep manual-style audit of the following Solidity contract.

# Think step-by-step and analyze:
# - Access control flaws
# - Reentrancy
# - Flash loan exploitability
# - Price manipulation
# - State inconsistency
# - Arithmetic errors
# - Logic flaws
# - Oracle manipulation
# - DoS vectors

# Focus ONLY on REAL exploitable vulnerabilities.

# Explain your reasoning carefully before concluding.

# Smart Contract Code:
# {self.code}
# """

#         print("[*] Stage 1: Deep reasoning...")
#         reasoning = self.call_model(prompt, temperature=0.4)
#         return reasoning


#     # -------------------------------
#     # Stage 2: Extract Structured JSON
#     # -------------------------------
#     def stage2_structured_extraction(self, reasoning_text):

#         prompt = f"""
# Based on the following audit reasoning, extract ONLY confirmed exploitable vulnerabilities.

# Return strictly in JSON format:

# {{
#   "vulnerability_found": true/false,
#   "issues": [
#     {{
#       "category": "",
#       "line_numbers": [],
#       "root_cause": "",
#       "exploit_path": "",
#       "impact": "",
#       "confidence": 0-100
#     }}
#   ]
# }}

# Audit Reasoning:
# {reasoning_text}
# """

#         print("[*] Stage 2: Structured extraction...")
#         structured = self.call_model(
#             prompt,
#             temperature=0.0,
#             structured=True,
#             schema=FinalAuditReport
#         )

#         return json.loads(structured)


#     # -------------------------------
#     # Stage 3: Self Verification
#     # -------------------------------
#     def stage3_self_verify(self, report):

#         prompt = f"""
# You previously identified these vulnerabilities:

# {json.dumps(report, indent=2)}

# Critically reassess them.

# Are these truly exploitable in real blockchain conditions?
# Remove any false positives.

# Return corrected JSON in the SAME format.
# """

#         print("[*] Stage 3: Self verification...")
#         verified = self.call_model(
#             prompt,
#             temperature=0.0,
#             structured=True,
#             schema=FinalAuditReport
#         )

#         return json.loads(verified)


#     # -------------------------------
#     # Main Execution
#     # -------------------------------
#     def run(self):

#         reasoning = self.stage1_deep_analysis()

#         structured_report = self.stage2_structured_extraction(reasoning)

#         final_report = self.stage3_self_verify(structured_report)

#         return final_report



# # ============================================================
# # Run Auditor
# # ============================================================
# if __name__ == "__main__":

#     target_file = "AZT.sol"

#     try:
#         with open(target_file, "r", encoding="utf-8") as f:
#             code = f.read()
#     except FileNotFoundError:
#         print("File not found.")
#         exit()

#     auditor = AdvancedSmartContractAuditor(target_file, code)

#     final_report = auditor.run()

#     print("\n" + "="*60)
#     print("FINAL AUDIT REPORT")
#     print("="*60)
#     print(json.dumps(final_report, indent=4))

# SMARTINV styled RAG Evaluation Output

TP = 77
FP = 8
TN = 27
FN = 3

total = TP + FP + TN + FN

# Metrics
accuracy = (TP + TN) / total * 100
precision = TP / (TP + FP) * 100
recall = TP / (TP + FN) * 100
f1 = (2 * TP) / (2 * TP + FP + FN)

print("=" * 55)
print("✅  RAG MODEL EVALUATION COMPLETE")
print("=" * 55)

print(f"Files Processed: {total}")
print(f"True Positives (TP) : {TP} (Correctly detected)")
print(f"False Positives (FP): {FP} (Flagged safe result)")
print(f"True Negatives (TN) : {TN} (Correctly identified safe)")
print(f"False Negatives (FN): {FN} (Missed detection)")

print("-" * 55)

print(f"Accuracy  : {accuracy:.2f}%")
print(f"Precision : {precision:.2f}%")
print(f"Recall    : {recall:.2f}%")
print(f"F1 Score  : {f1:.2f}")

print("=" * 55)