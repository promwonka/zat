import psycopg2
import threading
import pandas as pd
import numpy as np
import keras
import pickle
import time
import streamlit as st
from datetime import datetime

st.title("""
Forex Trader 
""")

ltsize = 1
multiplier = 1000

#connect to the db

conn = psycopg2.connect(
        host = "localhost",
        database = "corispsql_db",
        user = "corispsql",
        password = "coris@pc",
        port = 5432

)

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
    print('fund Updated')
    conn.commit()


def data_proc(thread_name,crr,param,model):


    
    i = 1
    h = 400
    l = 1

    model = keras.models.load_model(model)
    params = pickle.load(open(param, "rb"))

    mu = params["mu"]
    std = params["std"]

    time.sleep(10)

    c.execute("SELECT * FROM data WHERE currency = '%s'"%(crr))
    xdt = c.fetchall()
    conn.commit()
    lng = len(xdt)
    lng = lng/400 - 2
    print(lng)

    while i < lng :

        start = time.perf_counter()
        mn = l
        mx = h*i
        l = mx
        print(mn)
        print(mx)
        c.execute("SELECT * FROM data WHERE currency = '%s' and d_id BETWEEN '%s' and '%s'"%(crr,mn,mx))
        dt = c.fetchall()
        conn.commit()
        df = pd.DataFrame(dt, columns = ['d_id', 'UTC', 'AskPrice','BidPrice','AskVolume','BidVolume','currency'])
        df['UTC'] = pd.to_datetime(df['UTC'], errors='coerce')
        print(df.head(1))
        days = df.iloc[[300]].UTC.dt.dayofweek
        print('date = ', df.UTC[300])
        print(days)
        df = df.set_index('UTC')
        df.drop(['d_id', 'currency'], axis=1, inplace = True)
       
        print('fetched data')

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

        print ('generating lags')
        lags = 5
        cols = ["midprice","dir", "sma", "min", "max", "mom", "vol"]
        features = ["midprice","dir", "sma", "min", "max", "mom", "vol"]


        for f in features:
                for lag in range(1, lags + 1):
                    col = "{}_lag_{}".format(f, lag)
                    df[col] = df[f].shift(lag)
                    cols.append(col)
        df.dropna(inplace = True)

        print('fitting model')

        df_s = (df - mu) / std
        #pred = model.predict(df_s[cols])
        df_s

        print('Model fitted')

        df["proba"] = model.predict(df_s[cols])
        df["position"] = np.where(df.proba < 0.50, 0, np.nan) # 1. short where proba < 0.47
        df["position"] = np.where(df.proba > 0.60, 1, df.position) # 2. long where proba > 0.53
        df["position"] = df.position.ffill() # 4. in all other cases: hold position

        pmx = df.loc[df['proba'] > 0.6]
        pmx = pmx['midprice'].max()*multiplier


        dmax = df.loc[df['proba'] < 0.6]
        dmax = dmax['midprice'].max()*multiplier

        print('pmx  ======', pmx)

        finish = time.perf_counter()
        now = datetime.now()
        lsts = [0,1,2,3]

        if int(days) not in lsts :
            fx_trading(crr, 0,now,dmax,'not')

        else:
            fx_trading(crr, pmx,now,dmax,'ok')


        print(f'Finished in {round(finish-start,2)} second(s)')

        

        i = i+1



def fx_trading(crr, pmx,now,dmax,days):

    c.execute("SELECT * FROM holding WHERE currency = '%s' "%(crr))
    dfx = c.fetchone()
    conn.commit()
    print(crr)
    print(dfx)

    if days == 'ok':
    
        if dfx[1] < 20000:

            if pmx > 0:
                if dfx[2] < 10:

                    c.execute("INSERT INTO waitlist (type, amount, lot_size, currency, w_time) VALUES ('Buy','%s','%s','%s','%s' )" %(pmx,ltsize,crr,now))
                    print('-------------BUY------------------', dfx[2])
                    conn.commit()

                else:
                    pass
            else:
                pass
        
        else:
            pass



        c.execute("SELECT * FROM waitlist WHERE type = 'Buy' ")
        td = c.fetchone()
        conn.commit()

        if td != None:

            if td[1] == 'Buy':
                print(td[2])
                c.execute("UPDATE holding SET amount = amount + '%s' ,  lot_size = lot_size + 1 WHERE currency = '%s'" %(td[2],crr))
                conn.commit()
                c.execute("UPDATE  waitlist SET amount = '%s', type = 'Sell', w_time = '%s' WHERE w_id = '%s'"% ((td[2] + 0.001*multiplier),now, td[0]))
                conn.commit()
                print('**CONVERTED**------')
                ttime = datetime.now()
                c.execute("INSERT INTO tradelist (type,avg_price, lot_size, currency, t_time) VALUES ('Buy','%s','%s','%s','%s' )" %(td[2],ltsize,crr,ttime))
                print('-------------BUY------------------', dfx[2])
                conn.commit()

                fund_update(-td[2],crr)

            else:
                pass
        else:
            pass

        c.execute("SELECT * FROM waitlist WHERE type = 'Sell' ")
        ts = c.fetchone()
        conn.commit()
                
        if ts != None:
            if dfx[2] != 0 :

                if  (ts[2] >= dmax):
                    c.execute("UPDATE holding SET amount = amount - '%s',  lot_size = lot_size - 1 WHERE currency = '%s'" %(ts[2],crr))
                    conn.commit()
                    c.execute("DELETE FROM waitlist WHERE w_id = '%s'"% (ts[0]))
                    print('**-------------------------------------SELL-------------------------------**')
                    ttime = datetime.now()
                    c.execute("INSERT INTO tradelist (type,avg_price, lot_size, currency, t_time) VALUES ('Sell','%s','%s','%s','%s' )" %(ts[2],ltsize,crr,ttime))
                    fund_update(ts[2],crr)
                    conn.commit()

                else:
                    pass
            else: 
                pass
        else:
            pass

        
    else:
        print('hiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii')
        c.execute("SELECT * FROM waitlist WHERE type = 'Sell' ")
        ts = c.fetchone()
        conn.commit()
                
        if ts != None:
            if dfx[2] != 0 :

                #if (ts[2] >= dmax):
                c.execute("UPDATE holding SET amount = amount - '%s',  lot_size = lot_size - 1 WHERE currency = '%s'" %(ts[2],crr))
                conn.commit()
                c.execute("DELETE FROM waitlist WHERE w_id = '%s'"% (ts[0]))
                print('**-------------------------------------SELL-------------------------------**')
                ttime = datetime.now()
                c.execute("INSERT INTO tradelist (type,avg_price, lot_size, currency, t_time) VALUES ('Sell','%s','%s','%s','%s' )" %(ts[2],ltsize,crr,ttime))
                fund_update(ts[2],crr)
                conn.commit()

                # else:
                #     pass

            else:
                pass
        else: 
            pass


  
thread1 = threading.Thread(target=data_proc, args=("thread1", 'eurusd','paramsj4.pkl','DNN_modelj4.h5'))

# Start the threads
thread1.start()

thread1.join()


@st.cache
def load_data(crr):
    c.execute("SELECT * FROM tradelist WHERE currency = '%s'"%(crr))
    dt = c.fetchall()
    conn.commit()
    data = pd.DataFrame(dt, columns = ['ID', 'Type', 'Price','Lot Size','Currency','Time'])
    return data

@st.cache
def wait_data(crr):
    c.execute("SELECT * FROM waitlist WHERE currency = '%s'"%(crr))
    dt = c.fetchall()
    conn.commit()
    data = pd.DataFrame(dt, columns = ['ID', 'Type', 'Price','Lot Size','Currency','Time'])
    return data


st.write('Initial Amount = 20,000')

fv = fund_view('eurusd')
st.write('Total Remaining Amount',fv[2] )

wd = wait_data('eurusd')
lnwd = len(wd)
sumwd = wd['Price'].sum()

ld = load_data('eurusd')
lnld = len(ld)

st.write('Total Transactions',lnld)
st.write('Total round transactions = ', (lnld-lnwd)/2)
st.write('Total Profits',((lnld-lnwd)/2)*100)

st.write('Remaining amount available = ', fv[3])


st.write('Amount in waitlist = ', sumwd)

trade_data = load_data('eurusd')
wl_data = wait_data('eurusd')

st.subheader('Trade Data')
st.write(trade_data)

st.subheader('Waitlist Data')
st.write(wl_data)

df = pd.DataFrame(trade_data)
df.hist()


st.subheader('Raw Data')

c.execute("SELECT * FROM data WHERE currency = 'eurusd'")
dt = c.fetchall()
conn.commit()
df = pd.DataFrame(dt, columns = ['d_id', 'UTC', 'AskPrice','BidPrice','AskVolume','BidVolume','currency'])
df['UTC'] = pd.to_datetime(df['UTC'], errors='coerce')
df.drop(['d_id', 'currency'], axis=1, inplace = True)
df['Price'] = (df['AskPrice'] + df['BidPrice'])/2
df = df[['UTC','Price']].copy()

st.write(df[:200])
# st.line_chart(df)
