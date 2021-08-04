import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle
import keras
import asyncio
import streamlit as st
#import Trainer
#import Trader

def tr_process():

    st.write("""
    ## Forex Trader
    """)
    data = pd.read_csv("gbpusd.csv", parse_dates = ["UTC"], index_col = "UTC")
    data = data[:10000]
    print('fetched data')
    data['midprice'] = (data['AskPrice'] + data['BidPrice'])/2
    symbol = data.columns[0]
    data["returns"] = np.log(data[symbol] / data[symbol].shift())
    window = 50
    df = data.copy()
    df["dir"] = np.where(df["returns"] > 0, 1, 0)
    df["sma"] = df[symbol].rolling(window).mean() - df[symbol].rolling(150).mean()
    df["boll"] = (df[symbol] - df[symbol].rolling(window).mean()) / df[symbol].rolling(window).std()
    df["min"] = df[symbol].rolling(window).min() / df[symbol] - 1
    df["max"] = df[symbol].rolling(window).max() / df[symbol] - 1
    df["mom"] = df["returns"].rolling(3).mean()
    df["vol"] = df["returns"].rolling(window).std()
    df.dropna(inplace = True)

    lags = 6
    cols = []
    features = ["AskPrice","BidPrice","AskVolume","dir","midprice","BidVolume", "sma", "boll", "min", "max", "mom", "vol"]


    for f in features:
            for lag in range(1, lags + 1):
                col = "{}_lag_{}".format(f, lag)
                df[col] = df[f].shift(lag)
                cols.append(col)
    df.dropna(inplace = True)

    model = keras.models.load_model("DNN_model.h5")
    params = pickle.load(open("params.pkl", "rb"))

    mu = params["mu"]
    std = params["std"]
    df_s = (df - mu) / std
    pred = model.predict(df_s[cols])

    print('Model fitted')

    df["proba"] = model.predict(df_s[cols])
    df["position"] = np.where(df.proba < 0.51, -1, np.nan) # 1. short where proba < 0.47
    df["position"] = np.where(df.proba > 0.55, 1, df.position) # 2. long where proba > 0.53
    #test.index = test.index.tz_localize("UTC")
    df["NYTime"] = df.index.tz_convert("America/New_York")
    df["hour"] = df.NYTime.dt.hour
    df["position"] = np.where(~df.hour.between(2, 12), 0, df.position) # 3. neutral in non-busy hours
    df["position"] = df.position.ffill() # 4. in all other cases: hold position

    df_copy = df[['AskPrice', 'BidPrice', 'AskVolume','BidVolume', 'returns', 'dir','proba', 'position', 'NYTime', 'hour' ]].copy()
    df_copy.to_csv('hft_result.csv')


    print('Trading')

    fund = 100000
    alot = fund*0.20


    st.write('Initial Fund ',fund)
    st.write('Allotted trading fund ', alot)


    trade_cap = 1
    currencies = 4
    division = fund/currencies
    allocation = division/3


    allocation = 80

    df = pd.read_csv('hft_result.csv')
    df = df[:58000]
    gh = df['proba'] < 0.60
    gh.value_counts()
    df['midpoint'] = (df['AskPrice'] + df ['BidPrice'])/2


    ln = len(df)
    i = 0
    tr_num = 0

    buy_sum = 0
    buyq = 0
    bal = fund - alot
    df['Status'] = '-'


    while i < ln:
        
        pos = df.iloc[i]['proba']
        
        if  pos > 0.60 :

            if (alot > 0):
                df.loc[i,'trade'] = 'Buy'
                df.loc[i,'Cost Price'] = df.loc[i,'midpoint']
                
                if i%3 != 0:
                    alot = alot - 1000*df.loc[i,'midpoint']
                    tr_num = tr_num + 1
                    print('-----------------------Buy------------------')
                    buy_sum = buy_sum + df.loc[i,'midpoint']
                    print(df.loc[i,'midpoint'])
                    print('Balance')
                    print(alot)
                    print('-----')
                    df.loc[i,'Balance'] = alot
                    buyq = buy_sum/tr_num + 0.0010
                    # st.write('Bought ',df.loc[i,'midpoint'])
                    # st.write('Current Balance ',alot )

                    #print(buyq) 
                else:
                    df.loc[i,'Status'] = 'Rejected'
                    print('< Status >')
                    print(df.loc[i,'Status'])
                    

            else : 
                df.loc[i,'trade'] = 'Not'

                        
        elif pos < 0.52 :
            
            if (tr_num > 0): 
                
                if (buyq < (df.loc[i,'midpoint'])):
                    df.loc[i,'trade'] = 'Sell'
                    df.loc[i,'Sell Price'] = -(df.loc[i,'midpoint'])
                    
                    if i%3 != 0:
                        
                        alot = alot + 1000*df.loc[i,'midpoint']
                        tr_num = tr_num - 1
                        print('****Sell****')
                        buy_sum = buy_sum - (df.loc[i,'midpoint'])
                        print(df.loc[i,'midpoint'])
                        print('Balance')
                        print(alot)
                        df.loc[i,'Balance'] = alot
                        print('----')
                        # st.write('Sold ',df.loc[i,'midpoint'])
                    else:
                        df.loc[i,'Status'] = 'Rejected'
                        print('< Status >')
                        print(df.loc[i,'Status'])
                    
                else:
                    df.loc[i,'trade'] = 'Not'
                    
            else:
                df.loc[i,'trade'] = 'Not'
                
        else:
            df.loc[i,'trade'] = 'Not'
                
        fund = alot + bal
        alot = fund*0.20
        bal = fund - alot 
        
        i = i+1       
        
        


    df.to_csv('test.csv', index = False)


    df = pd.read_csv('test.csv')

    st.write("""
    ## Balance Chart
    """)
    st.line_chart(df.Balance)

    # st.line_chart(df.Status)

    fund = bal + alot

    st.write('Remaining Fund ',fund)
    st.write('Balance trading amount ', alot)

    #Trainer.mdtrainer()



tr_process()

