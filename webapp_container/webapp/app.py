from llama_index.core.workflow import Context
from agents import alfred, asyncio
from retriever import get_sql_data
from fastapi import FastAPI
from functions import set_token_usage_mlflow, compute_costs, get_best_prices_and_provider, get_span_attributes
from parameters import chat_llm_model_id, coding_llm_id, domain_guardrail_id
from models import domain_guardrail
from prompts import domain_guardrail_prompt
from judges import scorer_sampling, relevance_to_query_judge
from mlflow.genai.scorers import get_scorer
from mlflow.genai import list_scorers
import sys
import mlflow
import traceback
import inspect

app = FastAPI()

@mlflow.trace(name="agent_run")
async def run_agent(query):

    with mlflow.start_span(name="domain_guardrail", span_type="LLM") as span:
        response_domain_guardrail = domain_guardrail.complete(domain_guardrail_prompt(query))
           
        token_usage = set_token_usage_mlflow(response_domain_guardrail)
        
        costs = compute_costs(token_usage, domain_guardrail_id)
        
        provider = get_best_prices_and_provider(domain_guardrail_id)[0]
        
        span_attributes = get_span_attributes(token_usage, costs, provider, domain_guardrail_id)
        
        span.set_attributes(span_attributes)
        
        if str(response_domain_guardrail) != "relevant":
             return ("The question asked is not relevant !")

        
    # Creation of the SQL-RAG prompt
    with mlflow.start_span(name="sql_query", span_type="LLM") as span:
        prompt, token_usage = get_sql_data(query, top_n=3)
        
        costs = compute_costs(token_usage, coding_llm_id)
        
        provider = get_best_prices_and_provider(coding_llm_id)[0]

        span_attributes = get_span_attributes(token_usage, costs, provider, coding_llm_id)
        
        span.set_attributes(span_attributes)
    
    # Response from the agent
    with mlflow.start_span(name="llm_chat", span_type="AGENT") as span:
        response = await alfred.run(prompt)
    
        token_usage = set_token_usage_mlflow(response)
        
        costs = compute_costs(token_usage, chat_llm_model_id)
        
        provider = get_best_prices_and_provider(chat_llm_model_id)[0]

        span_attributes = get_span_attributes(token_usage, costs, provider, chat_llm_model_id)
        
        span.set_attributes(span_attributes)
    
    root_span = mlflow.get_current_active_span()
    
    relevance_to_query_judge_registered = get_scorer(name="relevance_to_query_judge_registered")
    
    
    feedback = relevance_to_query_judge_registered(
        inputs={"query": query},
        outputs=str(response)
    )
    
    assessment = mlflow.log_assessment(
        trace_id = root_span.trace_id,
        assessment=feedback
    )
 
        
    return response

@app.on_event("startup")
async def startup():
    # Setting the tracking URI for mlflow
    mlflow.set_tracking_uri("http://localhost:5001")
	    
    # Set experiment
    experiment = mlflow.set_experiment("rag_agent")
    
    # Setting correctness evaluation via a judge
    experiment_id = experiment.experiment_id
    
    # Register the judge if not already registered
    scorers = list_scorers(experiment_id=experiment_id)
    
    scores = [score.name for score in scorers]
    
    if "relevance_to_query_judge_registered" not in scores:
    
        relevance_to_query_judge_registered = relevance_to_query_judge.register(
            name="relevance_to_query_judge_registered", 
            experiment_id=experiment_id
        ) 

    # Activating autolog
    mlflow.llama_index.autolog()

@app.get("/predict/{query}")
async def main(query: str):

    try:
        with mlflow.start_run() as run:
            
            response = await run_agent(query)
            
            return {"query": query, "response": str(response)}

    except Exception as e:
    
        traceback.print_exc()
    	
        return {"error": str(e)}
