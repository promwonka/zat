import psycopg2
import time
import pandas as pd
import threading
from datetime import datetime

from  fix_application.py import new_market_order, order_status


conn = psycopg2.connect(
        host = "localhost",
        database = "corispsql_db",
        user = "corispsql",
        password = "coris@pc",
        port = 5432

)

c = conn.cursor()


multiplier = 1000
lsize = 1

def fund_view(crr):
    c.execute("SELECT * FROM FUND WHERE currency = '%s'" %crr)
    dt = c.fetchone()
    conn.commit()
    return dt


def fund_update(amt,crr):
    dt = fund_view(crr)
    x = 0.2
    av = dt[3]+amt
    to = dt[4]+av
    re = to*(1-x)
    av = to*x
    c.execute("UPDATE FUND SET av_amt = '%s',rem_amt = '%s' , amount = '%s'  WHERE currency = '%s'" %(av,re,to,crr)) 
    print('fund Updated')
    conn.commit()





def save_data(utc,askp,bidp,askv,bidv,curr):

    c.execute("INSERT INTO data2 (utc,askprice, bidprice, askvolume,bidvolume, currency) VALUES ('%s','%s','%s','%s','%s','%s')"%(utc,askp,bidp,askv,bidv,curr))
    conn.commit()


def place_order(nwid,price,ltsize,crr,type):

    if type == 'Buy':
        x = new_market_order(nwid,price,ltsize,crr,type) #expects only True/False as response
        if x == 'True':
             now = datetime.now()
             c.execute("INSERT INTO waitlist (type,w_id, amount, lot_size, currency, w_time) VALUES ('Buy','%s','%s','%s','%s','%s' )" %(nwid,price,ltsize,crr,now))
             print('-------------BUY------------------')
             new_price = price + 0.001
             place_order(nwid,new_price,ltsize,crr,'Sell')
        else:
            pass
    elif type == 'Sell':
        x = new_market_order(nwid,price,ltsize,crr,type) #expects only True/False as response
        if x == 'True':
             now = datetime.now()
             c.execute("INSERT INTO waitlist (type,w_id, amount, lot_size, currency, w_time) VALUES ('Buy','%s','%s','%s','%s','%s' )" %(nwid,price,ltsize,crr,now))
             print('-------------SELL------------------')
        else:
            pass

    else:
        print('something wrong happened')

    


def pp_order_status(crr):

     
     c.execute("SELECT * FROM waitlist WHERE currency = '%s'")
     wlist = c.fetchall()
     
     if wlist != None:

        df = pd.DataFrame(wlist, columns = ['w_id', 'type', 'amount','lotsize','currency','w_time'])
        ln = len(df)
        i = 0
        lastrow = df.iloc[ (ln-1) , : ]
        newid = lastrow[0]

        while i < ln :
            dfs = df.iloc[ i , : ]
            sts = order_status(dfs[0]) # expects 2 values as response 1- True/False and 2 - price of execution

            newid = newid + 1
            
            if sts[0] == 'True':
                
                if dfs[1] == 'Buy':
                    now = datetime.now()
                    c.execute("INSERT INTO tradelist (type,avg_price, lot_size, currency, t_time) VALUES ('Buy','%s','%s','%s','%s' )" %(sts[1],dfs[3],dfs[4],now))
                    print('*****************Bought*******************')
                    c.execute("UPDATE holding SET amount = amount + '%s' ,  lot_size = lot_size + 1 WHERE currency = '%s'" %(sts[1],crr))
                    conn.commit()
                    c.execute("UPDATE  waitlist SET amount = '%s', w_id = '%s' type = 'Sell', w_time = '%s' WHERE w_id = '%s'"% ((sts[1] + 0.001*multiplier),newid,now, dfs[0]))
                    conn.commit()
                    fund_update(-sts[1],crr)

                elif dfs[1] == 'Sell':

                    c.execute("UPDATE holding SET amount = amount - '%s',  lot_size = lot_size - 1 WHERE currency = '%s'" %(sts[1],crr))
                    conn.commit()
                    c.execute("DELETE FROM waitlist WHERE w_id = '%s'"% (dfs[0]))
                    print('******************************SOLD*********************************')
                    ttime = datetime.now()
                    c.execute("INSERT INTO tradelist (type,avg_price, lot_size, currency, t_time) VALUES ('Sell','%s','%s','%s','%s' )" %(sts[1],lsize,crr,ttime))
                    fund_update(sts[1],crr)
                    conn.commit()

                else:
                    print('something wrong')

            elif sts[0] == 'False':
                pass

            else:
                print('wrong info')

            i = i +1

     else:
         pass

     

    

