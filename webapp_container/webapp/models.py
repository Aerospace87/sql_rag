from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI
from transformers import AutoModelForSequenceClassification
import os

# get HF token
token = os.getenv('HF_TOKEN')


# HF main model to chat
chat_llm = HuggingFaceInferenceAPI(
    model_name="Qwen/Qwen2-7B-Instruct",
    token=token,
    temperature=1e-03,
    max_tokens=50,
    provider = "auto"
)


# HF model to write sql queries
coding_llm = HuggingFaceInferenceAPI(
    model_name="Qwen/Qwen2.5-Coder-32B-Instruct",
    token=token,
    temperature=1e-03,
    max_tokens=50,
    provider = "auto"
)

# HF model to rerank tables
reranker_model = AutoModelForSequenceClassification.from_pretrained(
    'jinaai/jina-reranker-v2-base-multilingual',
    dtype="auto",
    trust_remote_code=True,
)

reranker_model.to('cpu')

# Setting the model in the inference mode
reranker_model.eval()



