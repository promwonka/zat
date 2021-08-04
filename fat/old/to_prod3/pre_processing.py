import psycopg2
import time
import pandas as pd
import threading
from datetime import datetime
from db_connect import db_conn_fn

from  fix_application.py import new_market_order, order_status


conn = db_conn_fn()
c = conn.cursor()


multiplier = 10 #10 for microlots, 100 for mini lots, 1000 for a lot
pipc1 = 0.0003
pipc2 = 0.0005
# lsize = 1

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
    #print('fund Updated')
    conn.commit()



def place_order_buy(nwid,price,ltsize,crr,stime,etime):

    cntr = 0
    try:

        while cntr < 3:

            x = new_market_order(nwid,price,ltsize,crr,'Buy') #expects True/False and price as response
            if x[0] == 'True':
                x[1] = x[1]*multiplier
                now = datetime.now()
                c.execute("INSERT INTO tradelist (type,avg_price, lot_size, currency, t_time,stime,etime) VALUES ('Buy','%s','%s','%s','%s','%s','%s')" %(x[1],ltsize,crr,now,stime,etime))
                #print('*****************Bought*******************')
                c.execute("UPDATE holding SET amount = amount + '%s' ,  lot_size = lot_size + 1 WHERE currency = '%s'" %(x[1],crr))
                conn.commit()
                fund_update(-x[1],crr)
                break
            else:
                pass
    except Exception as e:
        print(str(e))
        print('failed while trying to place buy order')




def place_order_sell(nwid,price,ltsize,crr,slnt,stime,etime):

    cntr = 0
    try:

        while cntr < 3:
            c.execute("SELECT * FROM holding WHERE currency = '%s' "%(crr))
            dfx = c.fetchone()
            conn.commit()

            num = dfx[1]/dfx[2]

            if slnt == 0:

                if price > num + pipc1*multiplier : #pip control
                    x = new_market_order(nwid,price,ltsize,crr,'Sell') #expects True/False and price as response

                    if x == 'True':
                        x[1] = x[1]*multiplier
                        now = datetime.now()
                        c.execute("UPDATE holding SET amount = amount - '%s',  lot_size = lot_size - 1 WHERE currency = '%s'" %(x[1],crr))
                        conn.commit()
                        c.execute("INSERT INTO tradelist (type,avg_price, lot_size, currency, t_time,stime,etime) VALUES ('Sell','%s','%s','%s','%s','%s','%s')" %(x[1],ltsize,crr,now,stime,etime))
                        fund_update(x[1],crr)
                        conn.commit()
                        break

                    else:
                        cntr = cntr +1
                else: 
                    cntr = cntr +1

            elif slnt == 1:
                #current cmp 
                curr_cmp = 1
                if price >= num : 
                    x = new_market_order(nwid,price,ltsize,crr,'Sell') #expects True/False and price as response

                    if x == 'True':
                        x[1] = x[1]*multiplier
                        now = datetime.now()
                        c.execute("UPDATE holding SET amount = amount - '%s',  lot_size = lot_size - 1 WHERE currency = '%s'" %(x[1],crr))
                        conn.commit()
                        c.execute("INSERT INTO tradelist (type,avg_price, lot_size, currency, t_time,stime,etime) VALUES ('Sell','%s','%s','%s','%s','%s','%s')" %(x[1],ltsize,crr,now,stime,etime))
                        fund_update(x[1],crr)
                        conn.commit()
                        break

                    else:
                        cntr = cntr +1
                else: 
                    cntr = cntr +1

            elif slnt == 2:
                #current cmp 
                curr_cmp = 1
                if (price + pipc2*multiplier) <= num : #pip control
                    x = new_market_order(nwid,price,ltsize,crr,'Sell') #expects True/False and price as response

                    if x == 'True':
                        x[1] = x[1]*multiplier
                        now = datetime.now()
                        c.execute("UPDATE holding SET amount = amount - '%s',  lot_size = lot_size - 1 WHERE currency = '%s'" %(x[1],crr))
                        conn.commit()
                        c.execute("INSERT INTO tradelist (type,avg_price, lot_size, currency, t_time,stime,etime) VALUES ('Sell','%s','%s','%s','%s','%s','%s' )" %(x[1],ltsize,crr,now,stime,etime))
                        fund_update(x[1],crr)
                        conn.commit()
                        break

                    else:
                        cntr = cntr +1
                else: 
                    cntr = cntr +1

    except Exception as e:
        print(str(e))
        print('failed while trying to place Sell order')
            
            


    




    


# def pp_order_status(crr):

     
#      c.execute("SELECT * FROM waitlist WHERE currency = '%s'")
#      wlist = c.fetchall()
     
#      if wlist != None:

#         df = pd.DataFrame(wlist, columns = ['w_id', 'type', 'amount','lotsize','currency','w_time'])
#         ln = len(df)
#         i = 0
#         lastrow = df.iloc[ (ln-1) , : ]
#         newid = lastrow[0]

#         while i < ln :
#             dfs = df.iloc[ i , : ]
#             sts = order_status(dfs[0]) # expects 2 values as response 1- True/False and 2 - price of execution

#             newid = newid + 1
            
#             if sts[0] == 'True':
                
#                 if dfs[1] == 'Buy':
#                     now = datetime.now()
#                     c.execute("INSERT INTO tradelist (type,avg_price, lot_size, currency, t_time) VALUES ('Buy','%s','%s','%s','%s' )" %(sts[1],dfs[3],dfs[4],now))
#                     print('*****************Bought*******************')
#                     c.execute("UPDATE holding SET amount = amount + '%s' ,  lot_size = lot_size + 1 WHERE currency = '%s'" %(sts[1],crr))
#                     conn.commit()
#                     c.execute("UPDATE  waitlist SET amount = '%s', w_id = '%s' type = 'Sell', w_time = '%s' WHERE w_id = '%s'"% ((sts[1] + 0.001*multiplier),newid,now, dfs[0]))
#                     conn.commit()
#                     fund_update(-sts[1],crr)

#                 elif dfs[1] == 'Sell':

#                     c.execute("UPDATE holding SET amount = amount - '%s',  lot_size = lot_size - 1 WHERE currency = '%s'" %(sts[1],crr))
#                     conn.commit()
#                     c.execute("DELETE FROM waitlist WHERE w_id = '%s'"% (dfs[0]))
#                     print('******************************SOLD*********************************')
#                     ttime = datetime.now()
#                     c.execute("INSERT INTO tradelist (type,avg_price, lot_size, currency, t_time) VALUES ('Sell','%s','%s','%s','%s' )" %(sts[1],lsize,crr,ttime))
#                     fund_update(sts[1],crr)
#                     conn.commit()

#                 else:
#                     print('something wrong')

#             elif sts[0] == 'False':
#                 pass

#             else:
#                 print('wrong info')

#             i = i +1

#      else:
#          pass

     

    

