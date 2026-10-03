from transformers import AutoModelForSequenceClassification
from classes import HuggingFaceInferenceAPIwithTokenCount
from functions import get_best_prices_and_provider
from parameters import chat_llm_model_id, coding_llm_id, reranker_id, domain_guardrail_id, token
from prompts import domain_guardrail_prompt

# HF main model to chat
chat_llm = HuggingFaceInferenceAPIwithTokenCount(
    model_name=chat_llm_model_id,
    token=token,
    temperature=1e-03,
    max_tokens=50,
    provider=get_best_prices_and_provider(chat_llm_model_id)[0]
)


# HF model to write sql queries
coding_llm = HuggingFaceInferenceAPIwithTokenCount(
    model_name=coding_llm_id,
    token=token,
    temperature=1e-03,
    max_tokens=50,
    provider = get_best_prices_and_provider(chat_llm_model_id)[0]
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

# HF model to check if the input query is relevant
domain_guardrail = HuggingFaceInferenceAPIwithTokenCount(
    model_name=domain_guardrail_id,
    token=token,
    temperature=1e-03,
    max_tokens=50,
    provider = get_best_prices_and_provider(domain_guardrail_id)[0]
)












