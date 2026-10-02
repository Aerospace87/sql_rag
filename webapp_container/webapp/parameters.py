import os

# Models ids
chat_llm_model_id = "Qwen/Qwen2.5-Coder-32B-Instruct"
coding_llm_id = "Qwen/Qwen2.5-Coder-32B-Instruct"
reranker_id = "jinaai/jina-reranker-v2-base-multilingual"

# get HF token
token = os.getenv('HF_TOKEN')
