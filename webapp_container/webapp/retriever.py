import datasets
from llama_index.core.schema import Document
from functions import build_prompt, get_connection_details, run_query, rag_prompt, json, set_token_usage_mlflow
from reranker import table_declarations, rank_tables
from models import coding_llm
from guardrails import SQLGuardrail

def get_sql_data(query, top_n=2):
    try:
        top_n_tables_decl = rank_tables(query, table_declarations, top_n)
    except Exception as e:
        raise Exception("Ranking tables definition failed:\n{str(e)}")

    top_n_tables_decl = [table[1] for table in top_n_tables_decl]

    prompt = build_prompt(query, top_n_tables_decl)

    try:
        response = coding_llm.complete(prompt)
        token_usage = set_token_usage_mlflow(response)
            
    except Exception as e:
        raise Exception(f"Creation of sql query for RAG failed:\n{str(e)}")

    sql_query = str(response)\
        .replace("```sql", "")\
        .replace("```", "")
        
    check_query = SQLGuardrail(sql_query)
    
    if not check_query.allowed:
        raise Exception(check_query.reason)

    host, port, dbname, user, password = get_connection_details(
        mode="env",
        host_env="pg_host",
        port_env="pg_port",
        db_env="pg_db",
        user_env="pg_user",
        pwd_env ="pg_password"
    )

    sql_response = run_query(sql_query, host, port, dbname, user, password)

    json_table = json.dumps(sql_response)

    return rag_prompt(query, json_table, sql_query), token_usage

if __name__ == '__main__':
    query = "Identify the price of the most expensive article"

    print(get_sql_data(query, top_n=2))

