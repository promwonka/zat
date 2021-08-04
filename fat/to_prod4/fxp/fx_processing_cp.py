import psycopg2
import threading
import pandas as pd
import numpy as np
import keras
import pickle
import time
from datetime import datetime
import random
import string
from db_connect import db_conn_fn


ltsize = 1000
leverage = 100
multiplier = ltsize/leverage #10 for microlots, 100 for mini lots, 1000 for a lot
pipc1 = 0.0003
pipc2 = 0.0005

#connect to the db

conn = db_conn_fn()
c = conn.cursor()


#####################NEW
def tr_history_update(status,nwid,executed_price,executed_qty):
    print('hi')

    c.execute("UPDATE tr_history SET status = '%s', executed_price = '%s' ,executed_qty ='%s' WHERE order_id = '%s'"%(status,executed_price,executed_qty,nwid))
    conn.commit()

def fund_transaction(order_id,executed_price,executed_qty,crr,type):
    
    flag = 'S'
    try:
        amt = executed_price*multiplier
       # holding_value = executed_price*executed_qty

        if flag == 'S':
            
            if type == 'Buy':
                #buy 
                holding_value = executed_price*executed_qty
                c.execute("UPDATE holding SET amount = amount + '%s' ,  crncy_qty = crncy_qty + '%s' WHERE currency = '%s'" %(holding_value,executed_qty,crr))
                conn.commit()
                fund_update(-amt,crr)

            if type == 'Sell':
                #sell 
                c.execute("SELECT * FROM holding WHERE currency = '%s' "%(crr))
                dfx = c.fetchone()
                num = (dfx[1]/dfx[2])
                holding_value = num*executed_qty
                c.execute("UPDATE holding SET amount = amount - '%s' ,  crncy_qty = crncy_qty - '%s' WHERE currency = '%s'" %(holding_value,executed_qty,crr))
                conn.commit()
                fund_update(amt,crr)

            tr_history_update('Success',order_id,executed_price,executed_qty)

        elif flag == 'R':

            tr_history_update('Failed',order_id,executed_price,executed_qty)

    except Exception as e:
        print(str(e))
        print('failed while trying to update transactions')
####################NEW

#FUND

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


def tr_history_insert(nwid,type,avg_price,crncy_qty,t_time,stime,etime,crr):

    status = 'Pending'
    executed_price = 0
    executed_qty = 0

    c.execute("INSERT INTO tr_history (status,order_id,type,avg_price,executed_price,executed_qty,crncy_qty,t_time,stime,etime,currency) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" %(status,nwid, type, avg_price, executed_price,executed_qty, crncy_qty,t_time,stime,etime,crr))
    conn.commit()
   

def place_order_buy(nwid,price,ltsize,crr,stime,etime,bynt):

    try:
        if bynt == 1:
            now = datetime.now()
            c.execute("INSERT INTO tradelist (order_id,type,avg_price,crncy_qty,currency, t_time,stime,etime) VALUES ('%s','Buy','%s','%s','%s','%s','%s','%s')" %(nwid,price,ltsize,crr,now,stime,etime))
            conn.commit()
            tr_history_insert(nwid,'Buy', price, ltsize,now,stime,etime,crr)
            fund_transaction(nwid,price,ltsize,crr,'Buy')
        else:
            print('bynt = 0')

    except Exception as e:
        print(str(e))
        print('failed while trying to insert buy order')


def place_order_sell(nwid,price,ltsize,crr,slnt,stime,etime):

    print("Sell call")
    try:


        c.execute("SELECT * FROM holding WHERE currency = '%s' "%(crr))
        dfx = c.fetchone()
        num = (dfx[1]/dfx[2])

        print("NUMNUM",num)
        if slnt == 0:

            if price > num + pipc1 : #pip control
                print("INSIDE snlt==0")
                now = datetime.now()
                c.execute("INSERT INTO tradelist (order_id,type,avg_price,crncy_qty, currency, t_time,stime,etime) VALUES ('%s','Sell','%s','%s','%s','%s','%s','%s')" %(nwid,price,ltsize,crr,now,stime,etime))
                conn.commit()
                tr_history_insert(nwid,'Sell', price, ltsize,now,stime,etime,crr)
                fund_transaction(nwid,price,ltsize,crr,'Sell')
                    
            else:
                print("snlt==0",price,"num",num,"pipc1",pipc1)
                               
        elif slnt == 1:

            if price >=  num : #pip control
                print("INSIDE snlt==1") 
                now = datetime.now()
                c.execute("INSERT INTO tradelist (order_id,type,avg_price,crncy_qty, currency, t_time,stime,etime) VALUES ('%s','Sell','%s','%s','%s','%s','%s','%s')" %(nwid,price,ltsize,crr,now,stime,etime))
                conn.commit()
                tr_history_insert(nwid,'Sell', price, ltsize,now,stime,etime,crr)
                fund_transaction(nwid,price,ltsize,crr,'Sell')

            else: 
                print("snlt==1",price,"num",num,"pipc1",pipc1)

        else:
            print('out of sell loop')


   
    #    elif slnt == 2:
    #            print("snlt==2")
    #            if price >= num : 
    #                print("INSIDE snlt==2")
    #                now = datetime.now()
    #                c.execute("INSERT INTO tradelist (order_id,type,avg_price,crncy_qty, currency, t_time,stime,etime) VALUES ('%s','Sell','%s','%s','%s','%s','%s','%s')" %(nwid,price,ltsize,crr,now,stime,etime))
    #                conn.commit()
    #                tr_history_insert(nwid,'Sell', price, ltsize,now,stime,etime,crr)
    #                fund_transaction(nwid,price,ltsize,crr,'Sell')

    #            else: 
    #                print("snlt==2",price,"num",num,"pipc1",pipc1)

    except Exception as e:
        print(str(e))
        print('failed while trying to place Sell order')
            



def data_proc(thread_name,crr,param,model):

    model = keras.models.load_model(model)
    params = pickle.load(open(param, "rb"))

    mu = params["mu"]
    std = params["std"]

    #time.sleep(700)
    try:
        while True :

            start = time.perf_counter()
           # time.sleep(10)
            c.execute("SELECT * FROM data  WHERE currency = '%s' ORDER BY d_id DESC LIMIT 500 "%(crr))
            dt = c.fetchall()


            if len(dt) < 500:
                time.sleep(300)
                c.execute("SELECT * FROM data  WHERE currency = '%s' ORDER BY d_id DESC LIMIT 500 "%(crr))
                dt = c.fetchall()

            else:
                pass

            df = pd.DataFrame(dt, columns = ['d_id', 'UTC', 'AskPrice','BidPrice','AskVolume','BidVolume','currency'])
            df['UTC'] = pd.to_datetime(df['UTC'], errors='coerce')
            stime = df['UTC'].min()
            etime = df['UTC'].max()
            df.dropna(inplace = True)
            #print(df.head(1))
            days = df.iloc[[300]].UTC.dt.dayofweek
            #print('date = ', df.UTC[300])
            #print(days)
            df = df.set_index('UTC')
            df.drop(['d_id', 'currency'], axis=1, inplace = True)
        
            #print('fetched data')

            df['midprice'] = (df['AskPrice'] + df['BidPrice'])/2
            df = df[['midprice']].copy()
            symbol = df.columns[0]
            symbol
            df["returns"] = np.log(df[symbol] / df[symbol].shift(300))
            window = 50
            df["dir"] = np.where(df["returns"] > 0.0002, 1, 0)
            df["sma"] = df[symbol].rolling(window).mean() - df[symbol].rolling(150).mean()
            #df["boll"] = (df[symbol] - df[symbol].rolling(window).mean()) / df[symbol].rolling(window).std()
            df["min"] = df[symbol].rolling(window).min() / df[symbol] - 1
            df["max"] = df[symbol].rolling(window).max() / df[symbol] - 1
            df["mom"] = df["returns"].rolling(3).mean()
            df["vol"] = df["returns"].rolling(window).std()
            df.dropna(inplace = True)

            #print ('generating lags')
            lags = 5
            cols = ["midprice","dir", "sma", "min", "max", "mom", "vol"]
            features = ["midprice","dir", "sma", "min", "max", "mom", "vol"]


            for f in features:
                    for lag in range(1, lags + 1):
                        col = "{}_lag_{}".format(f, lag)
                        df[col] = df[f].shift(lag)
                        cols.append(col)
            df.dropna(inplace = True)

            #print('fitting model')

            df_s = (df - mu) / std
            #pred = model.predict(df_s[cols])
            df_s

            #print('Model fitted')

            df["proba"] = model.predict(df_s[cols])
            # df["position"] = np.where(df.proba < 0.50, 0, np.nan) # 1. short where proba < 0.47
            # df["position"] = np.where(df.proba > 0.60, 1, df.position) # 2. long where proba > 0.53
            # df["position"] = df.position.ffill() # 4. in all other cases: hold position
           # print(df.head(50))

           # print(df.tail(50))
            pmx = df.loc[df['proba'] > 0.7]
            byntd = len(pmx)
            print(byntd)
            pmx = pmx['midprice'].max()

            if byntd > 100:
                bynt = 1
            else:
                bynt = 0

            
            pmn = df.loc[df['proba'] <= 0.7]
            slntd = len(pmn)
            print(slntd)
            pmn = pmn['midprice'].max()


            if slntd > 100:
                slnt = 1
            else:
                slnt = 0


            finish = time.perf_counter()
            lsts = [0,1,2,3,4]

            if int(days) not in lsts :
                slnt = 2
                fx_trading(crr, 0,'not',pmn,slnt,stime,etime,bynt)

            else:
                fx_trading(crr, pmx,'ok',pmn,slnt,stime,etime,bynt)


            #print(f'Finished in {round(finish-start,2)} second(s)')

    except Exception as e:
        print('Model run error')
        print(str(e))





def fx_trading(crr, pmx,days,pmn,slnt,stime,etime,bynt):

    try:

        c.execute("SELECT * FROM holding WHERE currency = '%s' "%(crr))
        dfx = c.fetchone()
        # print(crr)
        # print(dfx)

        amt = pmx*multiplier

        if days == 'ok':
        
            if dfx[2] < ltsize:

                if pmx > 0:

                        c.execute("SELECT nextval('seq_id_gen_buy')")
                        v = c.fetchone()
                        nwid = v[0]
                        place_order_buy(nwid,pmx,ltsize,crr,stime,etime,bynt)
                        

                else:
                    pass
            
            else:
                pass




            if pmn > 0:
                if dfx[2] > 0:

                    c.execute("SELECT nextval('seq_id_gen_sell')")
                    v = c.fetchone()
                    nwid = v[0]
                    place_order_sell(nwid,pmn,ltsize,crr,slnt,stime,etime)
                    


                else:
                    pass
            else:
                pass
            

        else:
            #print('hiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii')
                            
            if pmn > 0:
                if dfx[2] > 0:
                    slnt = 2
                    c.execute("SELECT nextval('seq_id_gen_sell')")
                    v = c.fetchone()
                    nwid = v[0]
                    place_order_sell(nwid,pmn,ltsize,crr,slnt,stime,etime) 


                else:
                    pass
            else:
                pass

    except Exception as e:
        print('Order sending error')
        print(str(e))




try:
    thread1 = threading.Thread(target=data_proc, args=("thread1", 'EURUSD_','paramsj4.pkl','DNN_modelj4.h5'))
    print("hi here")
    # thread2 = threading.Thread(target=order_fetch, args=("thread2", 'eurusd'))

    # Start the threads
    thread1.start()
    # thread2.start()

    thread1.join()
    # thread2.join()

except Exception as e:
        print('Thread Error')
        print(str(e))

