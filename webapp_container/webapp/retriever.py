import datasets
from llama_index.core.schema import Document
from functions import build_prompt, get_connection_details, run_query, rag_prompt, json, set_token_usage_mlflow
from reranker import table_declarations, rank_tables
from models import coding_llm
#from mlflow import start_span
from guardrails import check_sql_query_not_malicious

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
        
    sql_query = check_sql_query_not_malicious(sql_query)

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

def get_data_from_semantic_search(query, collection_name, top_n=2, host="localhost", port=8000):
    chroma_client = HttpClient(host=host, port=port)

    collection = chroma_client.get_collection(name=collection_name)

    results = collection.query(
        query_texts=query,
        n_results=top_n
    )

    return results["documents"]



if __name__ == '__main__':
    query = "Identify the price of the most expensive article"

    print(get_sql_data(query, top_n=2))

