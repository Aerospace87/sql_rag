from llama_index.core.workflow import Context
from agents import alfred, asyncio
from retriever import get_sql_data
from fastapi import FastAPI
from functions import set_token_usage_mlflow, compute_costs, get_best_prices_and_provider
from parameters import chat_llm_model_id, coding_llm_id
import sys
import mlflow
import traceback
import inspect

app = FastAPI()

@mlflow.trace(name="agent_run")
async def run_agent(query):

    # Creation of the SQL-RAG prompt
    with mlflow.start_span(name="sql_query", span_type="LLM") as span:
        prompt, token_usage = get_sql_data(query, top_n=3)
        
        costs = compute_costs(token_usage, coding_llm_id)
        
        provider = get_best_prices_and_provider(coding_llm_id)[0]

        span.set_attribute("mlflow.chat.tokenUsage", token_usage)
        
        span.set_attribute("mlflow.llm.cost", costs)
        
        span.set_attribute("mlflow.llm.provider", provider)
    
    # Response from the agent
    with mlflow.start_span(name="llm_chat", span_type="AGENT") as span:
        response = await alfred.run(prompt)
    
        token_usage = set_token_usage_mlflow(response)
        
        costs = compute_costs(token_usage, chat_llm_model_id)
        
        provider = get_best_prices_and_provider(coding_llm_id)[0]

        span.set_attribute("mlflow.chat.tokenUsage", token_usage)
        
        span.set_attribute("mlflow.llm.cost", costs)
        
        span.set_attribute("mlflow.llm.provider", provider)
        
    return response

@app.on_event("startup")
async def startup():
    # Setting the tracking URI for mlflow
    mlflow.set_tracking_uri("http://localhost:5001")
	    
    # Set experiment
    mlflow.set_experiment("alfred-agent")

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
