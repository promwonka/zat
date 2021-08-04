import pandas as pd
import numpy as np
pd.set_option('display.float_format', lambda x: '%.5f' % x)
from DNNModel import *
import pickle
import time


def model_tn(ar):

    ln = len(ar)
    i =0
    while i < ln :

        start = time.perf_counter()

        print('reading data')
        data = pd.read_csv(ar[i],parse_dates = ["UTC"], index_col = "UTC")
        #data = data[:50000]

        print('creating features')
        data['midprice'] = (data['AskPrice'] + data['BidPrice'])/2
        symbol = data.columns[4]
        data["returns"] = np.log(data[symbol] / data[symbol].shift(300))
        window = 50
        df = data.copy()
        df["dir"] = np.where(df["returns"] > 0.002, 1, 0)
        df["sma"] = df[symbol].rolling(window).mean() - df[symbol].rolling(150).mean()
        df["boll"] = (df[symbol] - df[symbol].rolling(window).mean()) / df[symbol].rolling(window).std()
        df["min"] = df[symbol].rolling(window).min() / df[symbol] - 1
        df["max"] = df[symbol].rolling(window).max() / df[symbol] - 1
        df["mom"] = df["returns"].rolling(3).mean()
        df["vol"] = df["returns"].rolling(window).std()
        df.dropna(inplace = True)
        lags = 6
        cols = []
        features = ["midprice","dir","AskPrice","BidPrice","AskVolume","BidVolume", "sma", "boll", "min", "max", "mom", "vol"]
        for f in features:
            for lag in range(1, lags + 1):
                col = "{}_lag_{}".format(f, lag)
                df[col] = df[f].shift(lag)
                cols.append(col)
        df.dropna(inplace = True)
        split = int(len(df)*0.66)
        train = df.iloc[:split].copy()
        test = df.iloc[split:].copy()
        mu, std = train.mean(), train.std() 
        train_s = (train - mu) / std 

        print('fitting model')

        set_seeds(100)
        model = create_model(hl = 3, hu = 50, dropout = True, input_dim = len(cols))
        model.fit(x = train_s[cols], y = train["dir"], epochs = 50, verbose = False,validation_split = 0.2, shuffle = False, class_weight = cw(train))
        model.evaluate(train_s[cols], train["dir"]) 
        pred = model.predict(train_s[cols]) 

        print(f'dumping model')
        txt = ar[i]
        x = txt.split(".")
        model.save("DNN_model_%s.h5"%x[0])
        params = {"mu":mu, "std":std}
        pickle.dump(params, open("params_%s.pkl"%x[0], "wb"))

        i = i +1

        finish = time.perf_counter()
        print(f'{x[0]} - Finished in {round(finish-start,2)} second(s)')



    
