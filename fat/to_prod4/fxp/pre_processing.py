import psycopg2
import time
import pandas as pd
import threading
from datetime import datetime
from db_connect import db_conn_fn

conn = db_conn_fn()
c = conn.cursor()


multiplier = 10 #10 for microlots, 100 for mini lots, 1000 for a lot
pipc1 = 0.0003
pipc2 = 0.0005
# lsize = 1





            


