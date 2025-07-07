import psycopg2

def query_db_postgres(dburl:str ,query:str):
    try:
        conn = psycopg2.connect(dburl)
        cursor = conn.cursor()

        cursor.execute(query)

        rows = cursor.fetchall()
        print(rows)
        return rows
    except Exception as e:
        print("Error querying db")
        return []
    finally:
        cursor.close()
        conn.close()