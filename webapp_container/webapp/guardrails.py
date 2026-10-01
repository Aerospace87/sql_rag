from sqlglot import parse_one, exp

class SQLPolicy():
    """Class to specify a policy a sql query must respect"""
    
    not_allowed_operations:list = [
        "delete", "update", "drop", "insert", "alter", "create", "grant", "revoke", "truncate"
    ]
    not_allowed_tables: list = []
    not_allowed_columns: list = []
    row_limit: int = 3
    max_number_joins: int = 3
    max_number_subqueries: int  = 1
        
class SQLGuardrail():
    """Class checking if the provided query satisfies a list of expectations specified in a SQLPolicy object"""
    
    allowed: bool = True
    reason: str = ""  
     
    def __init__(self, sql_query: str, policy: SQLPolicy = SQLPolicy() ):      
        tree = parse_one(sql_query)
        
        error_dict = {}
        
        # Not allowed operations
        ops = {
           "drop": (exp.Drop, "Drop objects"),
           "delete": (exp.Delete, "Delete records"),
           "insert": (exp.Insert, "Insert reords"), 
           "update": (exp.Update, "Update records"), 
           "alter": (exp.Alter, "Modify the database objects"), 
           "create": (exp.Create, "Create the database objects"), 
           "grant": (exp.Grant, "Grant priviledges"), 
           "revoke": (exp.Revoke, "Revoke priviledges"),
           "truncate": (exp.TruncateTable, "Delete records")
        }
        
        # Check if the query implies any not allowed operation
        for key in policy.not_allowed_operations:
            if key in ops.keys():
                _, reason =  ops[key]
            
                if next(tree.find_all(_), None) is not None:
                    self.allowed = False
                    self.reason = f"{reason} is not allowed."
                    return 
        
        # Tables and/or columns not allowed to be queried           
        objs = {
            "table": (exp.Table, policy.not_allowed_tables),
            "column": (exp.Column, policy.not_allowed_columns)
        }
        
        
        # Check if the query involves any not allowed table or column
        for reason, (obj, not_allowed_elem) in objs.items():
            for elem in tree.find_all(obj):
                if elem.name in not_allowed_elem:
                    self.allowed = False
                    self.reason = f"Querying {reason} {elem.name} is not allowed."
                    return
                    
        cnts = {
            "Max number of joins": (exp.Join, policy.max_number_joins),
            "Max number of subqueries": (exp.Subquery, policy.max_number_subqueries)
        }

        # Check if the query and its result are too long
        for reason, (obj, max_count) in cnts.items():
            if sum(1 for _ in tree.find_all(obj)) > max_count:
                self.allowed = False
                self.reason = f"""{reason} is {max_count} instead {sum(1 for _ in tree.find_all(obj))} were provided.   
                \n{sql_query}"""
                return
                
          
        # Check the number of rows given by a limit statement in the query is less than the policy value
        limit = tree.find(exp.Limit)
        
        if limit and isinstance(limit.expression, exp.Literal):
           limit_value = int(limit.expression.this)
        else:
           limit_value = None
              
        if limit_value and policy.row_limit and limit_value > policy.row_limit:
                self.allowed = False
                self.reason = f"""The limit of records must be less than {policy.row_limit} instead {limit_value} was     
                provided.\n{sql_query}"""
                return  

 

if __name__ == "__main__":
    print("Unit test for not allowed operations")
    
    query = "truncate table customers"
    
    result = SQLGuardrail(query)

    if result.allowed:
        print("Test not passed")
    else:
        print("Test passed")
        
    print("Unit test for not allowed tables/columns")
    
    query = "select * from customers"
    
    policy = SQLPolicy()
    
    policy.not_allowed_tables = "customers"
    
    result = SQLGuardrail(query, policy)
    
    if result.allowed:
        print("Test not passed")
    else:
        print("Test passed")

    print("Unit test number of joins")
    
    query = """
	SELECT c.name, COUNT(o.id)
	FROM customers c
	JOIN orders o ON o.customer_id = c.id
	JOIN order_lines ol on o.order_line_id = ol.order_line
	WHERE   c.country = 'IT'
	GROUP BY c.name"""

    result = SQLGuardrail(query)

    if result.allowed:
        print("Test not passed")
    else:
        print("Test passed")
        
    print("Unit test for limit condition")
    
    query = "select * from customers limit 100"
    
    
    if result.allowed:
        print("Test not passed")
    else:
        print("Test passed")
    
    
