import datasets
from llama_index.core.schema import Document
from functions import build_prompt, get_connection_details, run_query, rag_prompt, json
from reranker import table_declarations, rank_tables
import agents


def load_guest_dataset() -> list:
    # Load the dataset
    guest_dataset = datasets.load_dataset("agents-course/unit3-invitees", split="train")

    # Convert dataset entries into Document objects
    docs = [
        Document(
            text="\n".join([
                f"Name: {guest_dataset['name'][i]}",
                f"Relation: {guest_dataset['relation'][i]}",
                f"Description: {guest_dataset['description'][i]}",
                f"Email: {guest_dataset['email'][i]}"
            ]),
            metadata={"name": guest_dataset['name'][i]}
        )
        for i in range(len(guest_dataset))
    ]

    return docs


def get_sql_data(query, top_n=2):
    try:
        top_n_tables_decl = rank_tables(query, table_declarations, top_n)
    except Exception as e:
        raise Exception("Ranking tables definition failed:\n{str(e)}")

    top_n_tables_decl = [table[1] for table in top_n_tables_decl]

    prompt = build_prompt(query, top_n_tables_decl)

    try:
        response = agents.llm.complete(prompt)
    except Exception as e:
        raise Exception("Creation of sql query for RAG failed:\n{str(e)}")

    sql_query = str(response)\
        .replace("```sql", "")\
        .replace("```", "")

    host, port, dbname, user, password = get_connection_details("../creds/cred.json", "testdb")

    sql_response = run_query(sql_query, host, port, dbname, user, password)

    if len(sql_response) == 0:
        raise Exception(f"The following sql query used to retrieve information did not return any result:\n{sql_query}")

    json_table = json.dumps(sql_response)

    return rag_prompt(query, json_table, sql_query)


if __name__ == '__main__':
    query = "Identify the most expensive article"

    print(get_sql_data(query, top_n=2))

