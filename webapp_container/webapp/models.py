from transformers import AutoModelForSequenceClassification
from classes import HuggingFaceInferenceAPIwithTokenCount
import os

# Models ids
chat_llm_model_id = "Qwen/Qwen2.5-Coder-32B-Instruct"
coding_llm_id = "Qwen/Qwen2.5-Coder-32B-Instruct"
reranker_id = "jinaai/jina-reranker-v2-base-multilingual"

# get HF token
token = os.getenv('HF_TOKEN')

# HF main model to chat
chat_llm = HuggingFaceInferenceAPIwithTokenCount(
    model_name=chat_llm_model_id,
    token=token,
    temperature=1e-03,
    max_tokens=50,
    provider="auto"
)


# HF model to write sql queries
coding_llm = HuggingFaceInferenceAPIwithTokenCount(
    model_name=coding_llm_id,
    token=token,
    temperature=1e-03,
    max_tokens=50,
    provider = "auto"
)

# HF model to rerank tables
reranker_model = AutoModelForSequenceClassification.from_pretrained(
    reranker_id,
    dtype="auto",
    trust_remote_code=True,
)

reranker_model.to('cpu')

# Setting the model in the inference mode
reranker_model.eval()



