import mlflow
import traceback
from fastapi import FastAPI
from mlflow.genai import list_scorers
from traces import run_agent
from mlflow import set_tracking_uri, set_experiment, start_run
from mlflow.llama_index import autolog
from judges import (
    scorer_sampling,
    relevance_to_query_judge, 
    retrieval_relevance_judge
)

app = FastAPI()

@app.on_event("startup")
async def startup():
    # Setting the tracking URI for mlflow
    set_tracking_uri("http://localhost:5001")
	    
    # Set experiment
    experiment = set_experiment("rag_agent")
    
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
        
    if "retrieval_relevance_judge_registered" not in scores:
        retrieval_relevance_judge_registered = retrieval_relevance_judge.register(
            name="retrieval_relevance_judge_registered",
            experiment_id=experiment_id
        )
        
    # Activating autolog
    autolog()

@app.get("/predict/{query}")
async def main(query: str):

    try:
        with start_run() as run:
            
            response = await run_agent(query)
            
            return {"query": query, "response": str(response)}
            

    except Exception as e:
    
        traceback.print_exc()
    	
        return {"error": str(e)}
