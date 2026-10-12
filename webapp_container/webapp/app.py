from llama_index.core.workflow import Context
from agents import alfred, asyncio
from retriever import create_prompt_for_sql_query, validate_sql_query, retrieve_data
from fastapi import FastAPI
from parameters import chat_llm_model_id, coding_llm_id, domain_guardrail_id
from models import domain_guardrail, coding_llm
from prompts import domain_guardrail_prompt
from mlflow.genai.scorers import get_scorer
from mlflow.genai import list_scorers
from functions import (
    set_token_usage_mlflow,
    compute_costs,
    get_best_prices_and_provider,
    get_span_attributes,
    rag_prompt,
    specify_span_attributes
)
from judges import (
    scorer_sampling,
    relevance_to_query_judge, 
    retrieval_relevance_judge
)
import sys
import mlflow
import traceback
import inspect

app = FastAPI()

@mlflow.trace(name="agent_run")
async def run_agent(query):

    with mlflow.start_span(name="domain_guardrail", span_type="LLM") as span:
        response_domain_guardrail = domain_guardrail.complete(domain_guardrail_prompt(query))
        
        # Setting span attributes
        specify_span_attributes(response_domain_guardrail, domain_guardrail_id, span)
        
        if str(response_domain_guardrail) != "relevant":
             return ("The question asked is not relevant !")
        
    # Creation of the SQL-RAG prompt
    with mlflow.start_span(name="sql_query", span_type="RETRIEVER") as span:
        sql_query_prompt = create_prompt_for_sql_query(query, top_n=3)

        response_sql_query_prompt = coding_llm.complete(sql_query_prompt)
        
        # Setting span attributes
        specify_span_attributes(response_sql_query_prompt, coding_llm_id, span)
        
        # Create and validate the query for the db
        
        sql_query = validate_sql_query(response_sql_query_prompt)
        
        # Retrieving data from db

        json_table = retrieve_data(sql_query)

        prompt = rag_prompt(query, json_table, sql_query)
        
    
    # Response from the agent
    with mlflow.start_span(name="llm_chat", span_type="AGENT") as span:
        response = await alfred.run(prompt)
        
        # Setting span attributes
        specify_span_attributes(response, chat_llm_model_id, span)

    # Evaluations
    root_span = mlflow.get_current_active_span()
    
    relevance_to_query_judge_registered = get_scorer(name="relevance_to_query_judge_registered")
    
    retrieval_relevance_judge_registered = get_scorer(name="retrieval_relevance_judge_registered")
    
    
    relevance_to_query_feedback = relevance_to_query_judge_registered(
        inputs={"query": query},
        outputs=str(response)
    )
    
    relevance_to_query_assessment = mlflow.log_assessment(
        trace_id = root_span.trace_id,
        assessment=relevance_to_query_feedback
    )
    
    retrieval_relevance_feedback = retrieval_relevance_judge_registered(
        inputs = {"inputs": query},
        outputs = {"outputs": json_table}
    )
            
    retrieval_relevance_assessment = mlflow.log_assessment(
        trace_id = root_span.trace_id,
        assessment=retrieval_relevance_feedback
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
        
    if "retrieval_relevance_judge_registered" not in scores:
        retrieval_relevance_judge_registered = retrieval_relevance_judge.register(
            name="retrieval_relevance_judge_registered",
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
