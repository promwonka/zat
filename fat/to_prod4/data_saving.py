import psycopg2
from datetime import datetime
from db_connect import db_conn_fn




conn = db_conn_fn()
c = conn.cursor()


def save_data(utc,askp,bidp,askv,bidv,curr):

    try:
        c.execute("INSERT INTO data (utc,askprice, bidprice, askvolume,bidvolume, currency) VALUES ('%s','%s','%s','%s','%s','%s')"%(utc,askp,bidp,askv,bidv,curr))
        conn.commit()
    except Exception as e:
        print('error while saving raw data')
        print(str(e))