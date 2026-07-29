from llama_index.core.workflow import Context
from agents import alfred, ToolCallResult, AgentStream, asyncio, debug_agent
from retriever import get_sql_data
from fastapi import FastAPI
import sys
import mlflow

app = FastAPI()

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

    # Creation of the SQL-RAG prompt
    prompt = get_sql_data(query, top_n=3)

    try:
        with mlflow.start_run():
            response = await alfred.run(prompt)

            print("🎩 Alfred's Response:")
            print(response)
            
            return {"query": query, "response": str(response)}

    except Exception as e:
        return {"error": str(e)}
