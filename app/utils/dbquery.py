from sqlalchemy.orm import Session


def query_db_postgres(db:Session ,query:str,params:dict=None):
    try:

        result = db.execute(query,params or {})
        rows = result.fetchall()

        return rows
    except Exception as e:
        print("Error executing the query")
        return []