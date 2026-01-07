from transformers import AutoModelForSequenceClassification
from typing import List, Tuple

reranker_model = AutoModelForSequenceClassification.from_pretrained(
    'jinaai/jina-reranker-v2-base-multilingual',
    dtype="auto",
    trust_remote_code=True,
)

reranker_model.to('cpu')

# Setting the model in the inference mode
reranker_model.eval()

# Tables DDLs
table_declarations = [
"""CREATE TABLE public.articoli (
	codart varchar(20) NOT NULL,
	descrizione varchar(60) DEFAULT NULL::character varying NULL,
	um bpchar(2) DEFAULT NULL::bpchar NULL,
	codstat varchar(20) DEFAULT NULL::character varying NULL,
	pzcart int2 NULL,
	pesonetto float8 NULL,
	idiva int4 NULL,
	idstatoart bpchar(1) DEFAULT NULL::bpchar NULL,
	datacreazione date NULL,
	idfamass int4 NULL,
	CONSTRAINT articoli_pkey PRIMARY KEY (codart),
	CONSTRAINT famassort_fk_articoli FOREIGN KEY (idfamass) REFERENCES public.famassort(id) ON UPDATE CASCADE,
	CONSTRAINT iva_fk_articoli FOREIGN KEY (idiva) REFERENCES public.iva(idiva)""",

"""CREATE TABLE public.barcode (
	codart varchar(20) NOT NULL,
	barcode varchar(13) NOT NULL,
	idtipoart varchar(2) NOT NULL,
	CONSTRAINT barcode_pkey PRIMARY KEY (barcode),
	CONSTRAINT articoli_fk_barcode FOREIGN KEY (codart) REFERENCES public.articoli(codart) ON DELETE CASCADE ON UPDATE CASCADE
);""",

"""CREATE TABLE public.dettlistini (
	id int4 NOT NULL,
	codart varchar(20) NOT NULL,
	idlist varchar(10) NOT NULL,
	prezzo numeric(8, 2) NOT NULL,
	CONSTRAINT dettlistini_pkey PRIMARY KEY (id),
	CONSTRAINT articoli_fk_dettlistini FOREIGN KEY (codart) REFERENCES public.articoli(codart) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_dettlistini_listini FOREIGN KEY (idlist) REFERENCES public.listini(id) ON DELETE CASCADE ON UPDATE CASCADE
);""",

"""CREATE TABLE public.listini (
	id varchar(10) NOT NULL,
	descrizione varchar(30) NOT NULL,
	obsoleto bpchar(2) NOT NULL,
	CONSTRAINT listini_pkey PRIMARY KEY (id)
);"""
]

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