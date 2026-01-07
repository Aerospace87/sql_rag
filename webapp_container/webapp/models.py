from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI
import os

# get HF token
token = os.getenv('HF_TOKEN')

# Initialize the Hugging Face model
llm = HuggingFaceInferenceAPI(
    model_name="Qwen/Qwen2.5-Coder-32B-Instruct",
    token=token,
    temperature=1e-03,
    max_tokens=50,
    provider = "auto"
)