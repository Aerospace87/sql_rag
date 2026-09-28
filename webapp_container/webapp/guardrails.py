def check_sql_query_not_malicious(sql_query):

    """Function to impede the running of malicious queries"""
    
    unsafe_ddl_ops = {
        "drop": "delete the database objects",
        "delete": "delete records",
        "insert": "insert new records", 
        "update": "update records", 
        "alter": "modify the database objects", 
        "create": "create the database objects", 
        "truncate": "delete records", 
        "grant": "grant priviledges", 
        "revoke": "revoke priviledges"
    }

    for word, reason in unsafe_ddl_ops.items():

        if word in sql_query.lower():
            raise Exception(f"Requests to {reason} are not allowed")
            
    return sql_query
    
