import psycopg2
import threading
import pandas as pd
import numpy as np
import keras
import pickle
import time
from datetime import datetime
#from pre_processing import place_order_buy,place_order_sell
from db_connect import db_conn_fn


ltsize = 1
multiplier = 10 #10 for microlots, 100 for mini lots, 1000 for a lot

#connect to the db

conn = db_conn_fn()
c = conn.cursor()


#FUND

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


def data_proc(thread_name,crr,param,model):

    #print('hi')

    model = keras.models.load_model(model)
    params = pickle.load(open(param, "rb"))

    mu = params["mu"]
    std = params["std"]

    #time.sleep(700)
    try:
        while True :

            #print('hi2x')

            start = time.perf_counter()
            time.sleep(1000)
            c.execute("SELECT * FROM data  WHERE currency = '%s' ORDER BY d_id DESC LIMIT 400 "%(crr))
            dt = c.fetchall()
            conn.commit()

            if len(dt) < 400:
                time.sleep(1000)
                c.execute("SELECT * FROM data  WHERE currency = '%s' ORDER BY d_id DESC LIMIT 400 "%(crr))
                dt = c.fetchall()
                conn.commit()
            else:
                pass

            df = pd.DataFrame(dt, columns = ['d_id', 'UTC', 'AskPrice','BidPrice','AskVolume','BidVolume','currency'])
            df['UTC'] = pd.to_datetime(df['UTC'], errors='coerce')
            stime = df['date'].min()
            etime = df['date'].max()
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
            df["dir"] = np.where(df["returns"] > 0.0001, 1, 0)
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
            df["position"] = np.where(df.proba < 0.50, 0, np.nan) # 1. short where proba < 0.47
            df["position"] = np.where(df.proba > 0.60, 1, df.position) # 2. long where proba > 0.53
            df["position"] = df.position.ffill() # 4. in all other cases: hold position

            pmx = df.loc[df['proba'] > 0.6]
            pmx = pmx['midprice'].max()*multiplier

            
            pmn = df.loc[df['proba'] < 0.5]
            pmn = pmn['midprice'].mean()*multiplier


            slntd = df.loc[df['proba'] < 0.5]
            slntd = len(slntd)

            if slntd > 100:
                slnt = 1
            else:
                slnt = 0

            # dmax = df.loc[df['proba'] < 0.6]
            # dmax = dmax['midprice'].max()*multiplier

            #print('pmx  ======', pmx)

            finish = time.perf_counter()
            lsts = [0,1,2,3]

            if int(days) not in lsts :
                slnt = 2
                fx_trading(crr, 0,'not',pmn,slnt,stime,etime)

            else:
                fx_trading(crr, pmx,'ok',pmn,slnt,stime,etime)


            #print(f'Finished in {round(finish-start,2)} second(s)')

    except Exception as e:
        print('Model run error')
        print(str(e))


        




def fx_trading(crr, pmx,days,pmn,slnt,stime,etime):

    try:

        c.execute("SELECT * FROM holding WHERE currency = '%s' "%(crr))
        dfx = c.fetchone()
        conn.commit()
        # print(crr)
        # print(dfx)

        if days == 'ok':
        
            if dfx[1] < 20000:

                if pmx > 0:
                    if dfx[2] < 1:

                        c.execute("SELECT * FROM tradelist WHERE currency = '%s' ORDER BY w_id DESC LIMIT 1")
                        wsid = c.fetchone()
                        conn.commit()
                        nwid = wsid[0]+1
                        place_order_buy(nwid,pmx,ltsize,crr,stime,etime)


                    else:
                        pass
                else:
                    pass
            
            else:
                pass




            if pmn > 0:
                if dfx[2] > 0:

                    c.execute("SELECT * FROM tradelist WHERE currency = '%s' ORDER BY w_id DESC LIMIT 1")
                    wsid = c.fetchone()
                    conn.commit()
                    nwid = wsid[0]+2
                    place_order_sell(nwid,pmn,ltsize,crr,slnt,stime,etime)


                else:
                    pass
            else:
                pass
            



        else:
            #print('hiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii')
                            
            if pmn > 0:
                if dfx[2] > 0:
                    slnt = 1
                    c.execute("SELECT * FROM tradelist WHERE currency = '%s' ORDER BY w_id DESC LIMIT 1")
                    wsid = c.fetchone()
                    conn.commit()
                    nwid = wsid[0]+2
                    place_order_sell(nwid,pmn,ltsize,crr,slnt,stime,etime)


                else:
                    pass
            else:
                pass

    except Exception as e:
        print('Order sending error')
        print(str(e))


    
    
# def order_fetch(thread_name,crr):
#     while True:
#         time.sleep(5)
#         print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
#         pp_order_status(crr)



try:
    thread1 = threading.Thread(target=data_proc, args=("thread1", 'eurusd','paramsj4.pkl','DNN_modelj4.h5'))
    # thread2 = threading.Thread(target=order_fetch, args=("thread2", 'eurusd'))

    # Start the threads
    thread1.start()
    # thread2.start()

    thread1.join()
    # thread2.join()

except Exception as e:
        print('Thread Error')
        print(str(e))


