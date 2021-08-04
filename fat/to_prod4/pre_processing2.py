import psycopg2
import time
import pandas as pd
from datetime import datetime
from db_connect import db_conn_fn


multiplier = 10


conn = db_conn_fn()
c = conn.cursor()

def fund_view(crr):
    c.execute("SELECT * FROM FUND WHERE currency = '%s'" %crr)
    dt = c.fetchone()
    return dt

def fund_update(amt,crr):
    dt = fund_view(crr)
    x = 0.2 #fund allocation percentage controller
    av = dt[3]+amt
    to = dt[4]+av
    re = to*(1-x)
    av = to*x
    c.execute("UPDATE FUND SET av_amt = '%s',rem_amt = '%s' , amount = '%s'  WHERE currency = '%s'" %(av,re,to,crr)) 
    #print('fund Updated')
    conn.commit()

def tr_history_update(status,nwid,executed_price,executed_qty):
    print('hi')

    c.execute("UPDATE tr_history SET status = '%s', executed_price = '%s' ,executed_qty ='%s' WHERE order_id = '%s'"%(status,executed_price,executed_qty,nwid))
    conn.commit()

def fund_transaction(flag,order_id,executed_price,executed_qty,crr,type):
    

    try:
        amt = executed_price*multiplier
        holding_value = executed_price*executed_qty

        if flag == 'S':
            
            if type == 'Buy':
                #buy 
                c.execute("UPDATE holding SET amount = amount + '%s' ,  crncy_qty = crncy_qty + '%s' WHERE currency = '%s'" %(holding_value,executed_qty,crr))
                conn.commit()
                fund_update(-amt,crr)

            if type == 'Sell':
                #sell 
                c.execute("UPDATE holding SET amount = amount + '%s' ,  crncy_qty = crncy_qty - '%s' WHERE currency = '%s'" %(holding_value,executed_qty,crr))
                conn.commit()
                fund_update(amt,crr)

            tr_history_update('Success',order_id,executed_price,executed_qty)

        elif flag == 'R':

            tr_history_update('Failed',order_id,executed_price,executed_qty)

    except Exception as e:
        print(str(e))
        print('failed while trying to update transactions')




        

        
     



