from transformers import AutoModelForSequenceClassification
from typing import List, Tuple
from functions import tables_definitions_in_the_schema

reranker_model = AutoModelForSequenceClassification.from_pretrained(
    'jinaai/jina-reranker-v2-base-multilingual',
    dtype="auto",
    trust_remote_code=True,
)

reranker_model.to('cpu')

# Setting the model in the inference mode
reranker_model.eval()

# Tables DDLs
table_declarations = tables_definitions_in_the_schema("public")

def rank_tables(query: str, tables_decl: List[str], top_n:int=0) -> List[Tuple[float, str]]:

    """Functions returning only the top_n most relevant table definitions for the query"""

    if top_n > len(tables_decl):
        raise ValueError(f"Error: top_n must be at max the number of table_definitions which is {str(len(tables_decl))} for the current case!")

    pairs = [[query, table_spec] for table_spec in tables_decl]

    scores = reranker_model.compute_score(pairs)

    tables_scores = list(zip(scores, tables_decl))

    tables_scores.sort(key=lambda x: x[0], reverse = True)

    return tables_scores[:top_n]

if __name__ == '__main__':
    query = "Identify the most expensive article"
    print(rank_tables(query, table_declarations, 2))