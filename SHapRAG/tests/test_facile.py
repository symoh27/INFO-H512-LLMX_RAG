import sys
import os
import torch
import numpy as np
from accelerate import Accelerator

# Add parent directory of SHapRAG to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from SHapRAG import ContextAttribution

# ----------------------------------------------------
# Mock classes for Hugging Face Transformers
# ----------------------------------------------------

class MockModelConfig:
    def __init__(self):
        self.eos_token_id = 2
        self.pad_token_id = 0

class MockModel(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.config = MockModelConfig()
        self.generation_config = MockModelConfig()
        
    def eval(self):
        pass
        
    def forward(self, input_ids, **kwargs):
        batch_size = input_ids.shape[0]
        seq_len = input_ids.shape[1]
        logits = torch.randn(batch_size, seq_len, 100)
        
        class MockOutput:
            def __init__(self, logits):
                self.logits = logits
        return MockOutput(logits)
        
    def generate(self, input_ids, **kwargs):
        batch_size = input_ids.shape[0]
        generated = torch.cat([
            input_ids, 
            torch.tensor([[10, 11, 12, 13, 2]], device=input_ids.device)
        ], dim=1)
        return generated

class MockBatchEncoding(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

class MockTokenizer:
    def __init__(self):
        self.pad_token = "<pad>"
        self.eos_token = "<eos>"
        self.pad_token_id = 0
        self.eos_token_id = 2
        
    def __call__(self, text, return_tensors=None, **kwargs):
        tokens = [1, 2, 3, 4, 5]
        if return_tensors == "pt":
            return MockBatchEncoding({
                "input_ids": torch.tensor([tokens]),
                "attention_mask": torch.tensor([[1, 1, 1, 1, 1]])
            })
        return tokens
        
    def apply_chat_template(self, messages, add_generation_prompt=False, tokenize=False):
        return " ".join([m["content"] for m in messages])
        
    def decode(self, token_ids, skip_special_tokens=False):
        return "assistant: This is a mock response from the LLM."

# ----------------------------------------------------
# Main Test Routine
# ----------------------------------------------------
def main():
    print("=== SHapRAG & FACILE Windows Compatibility Unit Tests ===")
    
    # 1. Setup mock models
    mock_model = MockModel()
    mock_tokenizer = MockTokenizer()
    accelerator = Accelerator()
    
    # 2. Dummy dataset
    items = [
        "Paragraph A: Paris is the capital of France.",
        "Paragraph B: London is the capital of the United Kingdom.",
        "Paragraph C: Berlin is the capital of Germany.",
        "Paragraph D: Rome is the capital of Italy."
    ]
    query = "What is the capital of France?"
    
    print("\n[Test 1] Initializing ContextAttribution with Mock LLM...")
    harness = ContextAttribution(
        items=items,
        query=query,
        prepared_model=mock_model,
        prepared_tokenizer=mock_tokenizer,
        accelerator=accelerator,
        verbose=True,
        utility_mode='log-perplexity'
    )
    print(f"ContextAttribution initialized successfully!")
    print(f"Target response: '{harness.target_response}'")
    
    # 3. Test utility function
    print("\n[Test 2] Testing get_utility...")
    subset = (1, 0, 0, 1)
    utility = harness.get_utility(subset, mode='log-perplexity')
    print(f"Utility for subset {subset}: {utility}")
    assert isinstance(utility, float), "Utility should be a float!"
    
    # 4. Test uniform/kernelshap sampling of ablations
    print("\n[Test 3] Testing ablated subset sampling...")
    sampled_uniform = harness._generate_sampled_ablations(num_samples=8, sampling_method="uniform", seed=42)
    print(f"Sampled uniform: {sampled_uniform}")
    assert len(sampled_uniform) == 8, f"Should sample exactly 8 items, got {len(sampled_uniform)}"
    
    sampled_kernel = harness._generate_sampled_ablations(num_samples=8, sampling_method="kernelshap", seed=42)
    print(f"Sampled kernelshap: {sampled_kernel}")
    assert len(sampled_kernel) == 8, f"Should sample exactly 8 items, got {len(sampled_kernel)}"
    
    # 5. Test ContextCite computation
    print("\n[Test 4] Testing ContextCite computation...")
    attributions_cc, fm_model_cc = harness.compute_contextcite(num_samples=8, seed=42)
    print(f"ContextCite attributions: {attributions_cc}")
    assert len(attributions_cc) == len(items), "Attributions length mismatch!"
    
    # 6. Test WSS/FACILE with Linear Surrogate
    print("\n[Test 5] Testing compute_wss with linear surrogate...")
    attributions_linear, extra_linear, fm_model_linear = harness.compute_wss(
        num_samples=8,
        seed=42,
        sampling_method="uniform",
        sur_type="linear"
    )
    print(f"Linear attributions: {attributions_linear}")
    assert len(attributions_linear) == len(items), "Linear attributions length mismatch!"
    
    # 7. Test WSS/FACILE with custom ALS FM on Windows
    print("\n[Test 6] Testing compute_wss with FM tuning (Windows ALS fallback)...")
    attributions_fm, extra_fm, fm_model_fm = harness.compute_wss(
        num_samples=16,
        seed=42,
        sampling_method="kernelshap",
        sur_type="fm_tuning",
        candidate_ranks=[1, 2],
        selection_metric="r2_delta"
    )
    print(f"FM tuning attributions: {attributions_fm}")
    print(f"FM interactions matrix: \n{extra_fm}")
    assert len(attributions_fm) == len(items), "FM attributions length mismatch!"
    assert extra_fm.shape == (len(items), len(items)), "FM interactions shape mismatch!"
    
    print("\n==============================================")
    print("ALL TESTS PASSED SUCCESSFULLY ON WINDOWS!")
    print("==============================================")

if __name__ == "__main__":
    main()
