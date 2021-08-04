import psycopg2

def db_conn_fn():

    conn = psycopg2.connect(
            host = "localhost",
            database = "corispsql_db",
            user = "corispsql",
            password = "coris@pc",
            port = 5432

    )

    return conn