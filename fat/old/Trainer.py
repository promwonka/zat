import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from DNNModel import *

plt.style.use("seaborn")
pd.set_option('display.float_format', lambda x: '%.5f' % x)


def mdtrainer():

    data = pd.read_csv('gbpusd.csv',parse_dates = ["UTC"], index_col = "UTC")
    #data = data[:100000]
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

    
    set_seeds(100)
    model = create_model(hl = 3, hu = 50, dropout = True, input_dim = len(cols))
    model.fit(x = train_s[cols], y = train["dir"], epochs = 50, verbose = False,
            validation_split = 0.2, shuffle = False, class_weight = cw(train))
    model.evaluate(train_s[cols], train["dir"]) 
    pred = model.predict(train_s[cols]) 

    import pickle

    #model.save("DNN_model.h5")
    params = {"mu":mu, "std":std}


    import keras
    #model = keras.models.load_model("DNN_model.h5")

