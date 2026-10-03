import os

# Models ids
chat_llm_model_id = "Qwen/Qwen2.5-Coder-32B-Instruct"
coding_llm_id = "Qwen/Qwen2.5-Coder-32B-Instruct"
reranker_id = "jinaai/jina-reranker-v2-base-multilingual"
domain_guardrail_id = "Qwen/Qwen3-4B-Instruct-2507"

# get HF token
token = os.getenv('HF_TOKEN')
