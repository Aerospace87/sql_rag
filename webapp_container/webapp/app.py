from llama_index.core.workflow import Context
from agents import alfred, asyncio
from retriever import get_sql_data
from fastapi import FastAPI
from functions import set_token_usage_mlflow
import sys
import mlflow
import traceback
import inspect

app = FastAPI()

@mlflow.trace(name="agent_run")
async def run_agent(query):

    # Creation of the SQL-RAG prompt
    prompt, token_usage = get_sql_data(query, top_n=3)
    span = mlflow.get_current_active_span()

    span.set_attribute("mlflow.chat.tokenUsage", token_usage)
    
    # Response from the agent
    response = await alfred.run(prompt)
        
    token_usage = set_token_usage_mlflow(response)
        
    span.set_attribute("mlflow.chat.tokenUsage", token_usage)
        
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
