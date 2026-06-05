system_prompt = """You are a helpful assistant that evaluates whether two answers express the same meaning.
 
You will be provided with:
- a question
- A ground truth answer
- A predicted answer
 
Your task is to compare them and determine if the **predicted answer conveys the same meaning** as the **ground truth answer**, even if it uses different words or more elaboration. Minor differences in phrasing, length, or detail are acceptable as long as the core meaning is preserved.
 
Your output must be one of the following:
- `True` — if the predicted answer has the same meaning as the ground truth answer.
- `False` — if the predicted answer significantly differs in meaning or introduces incorrect information.
 
Return **only** `True` or `False`. Do not include any explanations or extra text.
 
Example 1:
Question: What tempurature does the water boils?
Ground Truth Answer: "Water boils at 100 degrees Celsius."
Predicted Answer: "At 100°C, water reaches its boiling point."
Expected Output: True
 
Example 2:
Question: What is the capital of Japan
Ground Truth Answer: "The capital of Japan is Tokyo."
Predicted Answer: "Tokyo is the capital city of Japan."
Expected Output: True
 
Example 3:
Question: What is photosynthesis?
Ground Truth Answer: "Photosynthesis is how plants make food using sunlight."
Predicted Answer: "Photosynthesis helps animals digest food using sunlight."
Expected Output: False
 
Example 4:
Question: What was the outcome of the race?
Ground Truth Answer: "She won the race."
Predicted Answer: "She participated in the race."
Expected Output: False
 
Do not provide explanations—only output `True` or `False`."""
 
try:
    import os
    from typing import Optional
    from openai import OpenAI
    
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

    class OpenRouterClient:
        def __init__(self, api_key: str = OPENROUTER_API_KEY, model: str = "meta-llama/llama-3.3-70b-instruct"):
            self.api_key = api_key
            if not self.api_key:
                import warnings
                warnings.warn("[!] Attention: Clé API OpenRouter non configurée.")
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key,
                default_headers={
                    "HTTP-Referer": "https://colab.research.google.com/",
                    "X-Title": "TEKNO AutoRAG Belgium"
                }
            )
            self.default_model = model
            
        def chat(self, prompt: str, model: Optional[str] = None, system_prompt: str = "You are a helpful assistant.", temperature=0.0) -> str:
            selected_model = model or self.default_model
            try:
                response = self.client.chat.completions.create(
                    model=selected_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=4096,
                    temperature=temperature
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                import warnings
                warnings.warn(f"OpenRouter query failed: {e}")
                return "False"

    or_client = OpenRouterClient()
except Exception as e:
    or_client = None
    import warnings
    warnings.warn(f"OpenRouter client could not be initialized: {e}")
  
def prompt_just_text(prompt: str,temperature=0.0) -> str:
    if or_client is None:
        return "False"
    return or_client.chat(
        prompt=prompt,
        system_prompt=system_prompt,
        temperature=temperature
    )
 
 
results = []
def evaluate(question: str, provided: str, ground_truth:str):
    template_prompt = f"""Evaluate the provided answer using the ground truth answer, is the provided answer correct?:
    Question:{question}
    Provided answer: {provided}
    Ground Truth: {ground_truth}"""
   
    response = prompt_just_text(template_prompt)
    return response
 
 