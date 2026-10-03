import simplejson as json
from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from decimal import Decimal
from datetime import date
from prompts import build_prompt, rag_prompt
import requests

def get_connection_details(
        mode=None,
        connection_file=None,
        source_name=None,
        host_env=None,
        port_env=None,
        db_env=None,
        user_env=None,
        pwd_env =None
    ):
    """Function to read postgres db connection details from file"""
    if mode == "file":
        # In case connections details are provided through a json file
        try:
            with open(connection_file, 'r') as fh:
                data = json.load(fh)
        except Exception as e:
            import os
            dirs = os.listdir(os.getcwd())
            raise Exception(f"The file {connection_file} not in the folder. The following files are present:\n{dirs}")

        for source in data["sources"]:
            if source["source_name"] == source_name:
                return source["host"], source["port"], source["dbname"], source["user"], source["password"]

    elif mode == "env":
        # In case connections details are provided via environment variables
        import os

        host = os.getenv(host_env)
        port = os.getenv(port_env)
        dbname = os.getenv(db_env)
        user = os.getenv(user_env)
        pwd = os.getenv(pwd_env)
        return host, port, dbname, user, pwd

    else:
        raise ValueError(f"The mode inserted ({mode}) is not supported. Please choose between 'env' and 'file'")

def run_query(query, host, port, dbname, user, password):
    """Function running a query on the database"""
    conn = connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password
    )

    cur = conn.cursor(cursor_factory=RealDictCursor)

    res = cur.execute(query)

    return cur.fetchall()

def get_ddl_query(table_schema, table_name):
    ddl_query = f"""
with cols as (
select
	c.column_name,
	case
		when c.data_type like 'character%' then concat(c.udt_name, '(', character_maximum_length , ')')
		else c.udt_name
	end as full_data_type,
	case
		when column_default is not null then concat('DEFAULT', ' ', column_default)
		else ''
		end as default,
	case
		when c.is_nullable = 'YES' then 'NULL'
		else 'NOT NULL'
	end as nullable
	from information_schema.columns c
	where table_schema = '{table_schema}' and table_name = '{table_name}'
	order by ordinal_position asc
),
cols_final as (
	select
		string_agg(concat(c.column_name, ' ', c.full_data_type, ' ', c.default, ' ', c.nullable), ',\n') as lin
	from cols c
),
pk_and_fk as(
	select
		contype as costraint_type,
		conrelid::regclass AS table_from,
    	conname as constraint_name,
    	pg_get_constraintdef(oid) as costraint_definition
from   pg_catalog.pg_constraint
where  contype IN ('f', 'p ') AND connamespace = '{table_schema}'::regnamespace and conrelid::regclass::text = '{table_name}'
order by 
	conrelid::regclass ,
	contype DESC
),
pk_and_fk_final as(
	select
		string_agg(concat('CONSTRAINT', ' ', pf.constraint_name, ' ', pf.costraint_definition), ',\n') as lin
	from pk_and_fk pf
),
unio as (
	select
		1 as ord,
		lin 
	from cols_final
	union
	select
		2 as ord,
		lin 
	from pk_and_fk_final
	order by ord
)
select
	concat('CREATE TABLE {table_schema}.{table_name} (\n',string_agg(lin, ',\n'), '\n)') as ddl
from unio"""
    return ddl_query

def get_ddl_table(
        table_schema,
        table_name,
        mode="env",
        connection_file=None,
        source_name=None,
        host_env="pg_host",
        port_env="pg_port",
        db_env="pg_db",
        user_env="pg_user",
        pwd_env="pg_password"):

    ddl_query = get_ddl_query(table_schema, table_name)

    host, port, dbname, user, password = get_connection_details(
        mode=mode,
        connection_file=connection_file,
        source_name=source_name,
        host_env=host_env,
        port_env=port_env,
        db_env=db_env,
        user_env=user_env,
        pwd_env =pwd_env
    )

    try:
        result = run_query(ddl_query, host, port, dbname, user, password)

    except Exception as e:
        raise Exception(f"Error: the table {table_schema}.{table_name} has not been found.Details:\n{str(e)}")

    return result[0]["ddl"]

def get_tables_in_schema_query(table_schema):
    query = f"""
select 
	table_name 
from information_schema.tables
where table_schema = '{table_schema}'    
    """

    return query

def get_tables_in_schema(table_schema, mode, connection_file, source_name, host_env, port_env, db_env, user_env, pwd_env):
    query = get_tables_in_schema_query(table_schema)

    host, port, dbname, user, password = get_connection_details(
        mode=mode,
        connection_file=connection_file,
        source_name=source_name,
        host_env=host_env,
        port_env=port_env,
        db_env=db_env,
        user_env=user_env,
        pwd_env =pwd_env
    )

    try:
        result = run_query(query, host, port, dbname, user, password)

    except Exception as e:
        raise Exception(f"Error: the schema {table_schema} ad a problem.Details:\n{str(e)}")

    return result

def tables_definitions_in_the_schema(
        table_schema,
        mode="env",
        connection_file=None,
        source_name=None,
        host_env="pg_host",
        port_env="pg_port",
        db_env="pg_db",
        user_env="pg_user",
        pwd_env="pg_password"
):

    tables = get_tables_in_schema(table_schema, mode, connection_file, source_name, host_env, port_env, db_env, user_env, pwd_env)

    ddls = []
    for table in tables:

        ddl_table = get_ddl_table(table_schema, table["table_name"], mode, connection_file, source_name, host_env, port_env, db_env, user_env, pwd_env)

        ddls.append(ddl_table)

    return ddls
    
def get_table_description_query(schema, table):
    
    query = f"""
SELECT
    c.relname AS table_name,
    obj_description(c.oid) AS table_description
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind = 'r'
AND n.nspname = '{schema}' AND c.relname = '{table}'
    """
    
    
    return query
    
    
def get_table_description(schema, table):
    """Obtains descriptions of a table in a schema."""
    
    query = get_tables_description_query(tables_dict)

    host, port, dbname, user, password = get_connection_details(
        mode=mode,
        connection_file=connection_file,
        source_name=source_name,
        host_env=host_env,
        port_env=port_env,
        db_env=db_env,
        user_env=user_env,
        pwd_env =pwd_env
    )

    try:
        result = run_query(query, host, port, dbname, user, password)

    except Exception as e:
        raise Exception(f"Error: The retrieval of information about the following tables failed:{'\n'.join(tables.values())} failed. Details:\n{str(e)}")

    return result
    
def get_columns_description_query(schema, table):
    query = f"""
SELECT
    cols.column_name,
    pgd.description as column_description
FROM pg_catalog.pg_statio_all_tables st
JOIN information_schema.columns cols
  ON cols.table_schema = st.schemaname
 AND cols.table_name = st.relname
LEFT JOIN pg_catalog.pg_description pgd
  ON pgd.objoid = st.relid
 AND pgd.objsubid = cols.ordinal_position
WHERE cols.table_schema = '{schema}' and cols.table_name = '{table}'
ORDER BY cols.ordinal_position;
    """
    
    return query
    
def get_columns_description(schema:str, table: str):
    query = get_columns_description_query(schema, table)

    host, port, dbname, user, password = get_connection_details(
        mode=mode,
        connection_file=connection_file,
        source_name=source_name,
        host_env=host_env,
        port_env=port_env,
        db_env=db_env,
        user_env=user_env,
        pwd_env =pwd_env
    )

    try:
        result = run_query(query, host, port, dbname, user, password)

    except Exception as e:
        raise Exception(f"Error: The retrieval of columns information about the table {schema}.{table} failed. Details:\n{str(e)}")

    return result

def set_token_usage_mlflow(response):
    """Function to set the mlflow attribute to show token consumption in the ui"""
    
    if response.raw.usage is not None:    
        usage = response.raw.usage
    
        token_usage = {
            "input_tokens": usage.prompt_tokens,
            "output_tokens": usage.completion_tokens,
            "total_tokens": usage.total_tokens
        }
    else:
        token_usage = {}
    
            
    return token_usage

def get_providers(model_id):

    """Get information about model provider"""
    
    url = f"https://router.huggingface.co/v1/models/{model_id}"

    response = requests.get(url).json()
    
    if response.get("error"):
       raise Exception(response["error"])
    
    return response["data"]["providers"]


def get_best_prices_and_provider(model_id):

    """Finds the provider with minimum input costs per mln of tokens"""
    
    providers = get_providers(model_id)

    min_input_price = None
    output_price = None
    provider = ""

    for idx, p in enumerate(providers):
        if p["status"] == "live" and p.get("pricing", False):
    
            provider_input_price = p["pricing"]["input"]
            provider_output_price = p["pricing"]["output"]
        
            if min_input_price is None:
                min_input_price = provider_input_price
                output_price = provider_output_price
                provider = p["provider"]
            elif min_input_price and provider_input_price < min_input_price:
                min_input_price = provider_input_price
                output_price = provider_output_price
                provider = p["provider"]
           
        
    return provider, min_input_price, output_price
    
    
def compute_costs(token_usage, model_id):

    prov, input_price, output_price = get_best_prices_and_provider(model_id)

    costs = {
        "input_cost": token_usage["input_tokens"] * (input_price/1000000),
        "output_cost": token_usage["output_tokens"] * (output_price/1000000),
        "total_cost": token_usage["input_tokens"] * (input_price/1000000) + token_usage["output_tokens"] *   
                             (output_price/1000000)
    }
                
    return costs
    
def get_span_attributes(token_usage, costs, provider, model_id):
    """Returns with a dictionary with the span attributes of interest"""
    
    span_attributes = {
            "mlflow.chat.tokenUsage": token_usage,
            "mlflow.llm.cost": costs,
            "mlflow.llm.provider": provider,
            "mlflow.llm.model": model_id
    }
    
    return span_attributes
        
if __name__ == "__main__":
    print(build_prompt("ciao", ["a", "b"]))

    print(tables_definitions_in_the_schema("public"))
