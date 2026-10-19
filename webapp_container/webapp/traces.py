import mlflow
from models import domain_guardrail, coding_llm
from prompts import domain_guardrail_prompt
from parameters import chat_llm_model_id, coding_llm_id, domain_guardrail_id
from retriever import create_prompt_for_sql_query, validate_sql_query, retrieve_data
from mlflow.genai.scorers import get_scorer
from agents import alfred, asyncio
from functions import (
    set_token_usage_mlflow,
    compute_costs,
    get_best_prices_and_provider,
    get_span_attributes,
    rag_prompt,
    specify_span_attributes,
    specify_root_trace_attributes
)


@mlflow.trace(name="domain_guardrail", span_type="LLM")
def run_domain_guardrail(query):
    response_domain_guardrail = domain_guardrail.complete(domain_guardrail_prompt(query))
    
    # Setting span attributes
    span = mlflow.get_current_active_span()
    specify_span_attributes(response_domain_guardrail, domain_guardrail_id, span)
    
    return response_domain_guardrail
        
 
@mlflow.trace(name="sql_query", span_type="RETRIEVER")
def sql_query(query, top_n=3):
    sql_query_prompt = create_prompt_for_sql_query(query, top_n=top_n)

    response_sql_query_prompt = coding_llm.complete(sql_query_prompt)
        
    # Setting span attributes
    span = mlflow.get_current_active_span()
    specify_span_attributes(response_sql_query_prompt, coding_llm_id, span)
        
    # Create and validate the query for the db    
    sql_query = validate_sql_query(response_sql_query_prompt)
        
    # Retrieving data from db
    json_table = retrieve_data(sql_query)
    
    prompt = rag_prompt(query, json_table, sql_query)
    
    return prompt, json_table, response_sql_query_prompt
    
@mlflow.trace(name="llm_chat", span_type="AGENT")
async def llm_chat(prompt):
    response = await alfred.run(prompt)
        
    # Setting span attributes
    span = mlflow.get_current_active_span()
    specify_span_attributes(response, chat_llm_model_id, span)

    return response

@mlflow.trace(name="agent_run")
async def run_agent(query):

    response_domain_guardrail = run_domain_guardrail(query)
    
    if str(response_domain_guardrail) != "relevant":
       return ("The question asked is not relevant !")

    prompt, json_table, response_sql_query_prompt = sql_query(query, top_n=3)
    
    response = await llm_chat(prompt)

    response_list = [
        (response_domain_guardrail, domain_guardrail_id),
        (response_sql_query_prompt, coding_llm_id),
        (response, chat_llm_model_id)
    ]

    # Total costs and token counts 
    root_span = mlflow.get_current_active_span()
    specify_root_trace_attributes(response_list, root_span)


    # Evaluations
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
