
import pandas as pd
import numpy as np
import tpqoa
import pickle
from datetime import datetime, timedelta

class DNNTrader(tpqoa.tpqoa):
    def __init__(self, conf_file, instrument, bar_length, window, lags, units, model, mu, std):
        super().__init__(conf_file)
        self.position = 0
        self.instrument = instrument
        self.window = window
        self.bar_length = bar_length
        self.lags = lags
        self.units = units
        self.model = model
        self.mu = mu
        self.std = std
        self.tick_data = pd.DataFrame()
        self.hist_data = None
        self.min_length = None
        self.raw_data = None
        self.data = None
        self.profits = [] 
        
    def get_most_recent(self, days = 5):
        now = datetime.utcnow()
        now = now - timedelta(microseconds = now.microsecond)
        past = now - timedelta(days = days)
        df = self.get_history(instrument = self.instrument, start = past, end = now,
                               granularity = "S5", price = "M").c.dropna().to_frame()
        df.rename(columns = {"c":self.instrument}, inplace = True)
        df.index = df.index.tz_localize("UTC")
        df = df.resample(self.bar_length, label = "right").last().dropna().iloc[:-1]
        self.hist_data = df.copy()
        self.min_length = len(self.hist_data) + 1
        
    def resample_and_join(self):
        self.raw_data = self.hist_data.append(self.tick_data.resample(self.bar_length, 
                                                                  label="right").last().ffill().iloc[:-1]) 
    
    def prepare_data(self):
        # create features 
        df = self.raw_data.copy()
        df["returns"] = np.log(df[self.instrument] / df[self.instrument].shift())
        df["dir"] = np.where(df["returns"] > 0, 1, 0)
        df["sma"] = df[self.instrument].rolling(self.window).mean() - df[self.instrument].rolling(150).mean()
        df["boll"] = (df[self.instrument] - df[self.instrument].rolling(self.window).mean()) / df[self.instrument].rolling(self.window).std()
        df["min"] = df[self.instrument].rolling(self.window).min() / df[self.instrument] - 1
        df["max"] = df[self.instrument].rolling(self.window).max() / df[self.instrument] - 1
        df["mom"] = df["returns"].rolling(3).mean()
        df["volat"] = df["returns"].rolling(self.window).std()
        df.dropna(inplace = True)
        
        # create lags
        self.cols = []
        features = ["dir", "sma", "boll", "min", "max", "mom", "volat"]

        for f in features:
            for lag in range(1, self.lags + 1):
                col = "{}_lag_{}".format(f, lag)
                df[col] = df[f].shift(lag)
                self.cols.append(col)
        df.dropna(inplace = True)
        self.data = df.copy()

    def predict(self):
        df = self.data.copy()
        df_s = (df - self.mu) / self.std
        df["proba"] = self.model.predict(df_s[self.cols])
        self.data = df.copy()
        
    def on_success(self, time, bid, ask):
        print(self.ticks, end = " ")
        
        # store and resample tick data and join with historical data
        df = pd.DataFrame({self.instrument:(ask + bid)/2}, 
                          index = [pd.to_datetime(time)])
        self.tick_data = self.tick_data.append(df)
        self.resample_and_join()
        
        # only if new bar has been added:
        if len(self.raw_data) > self.min_length - 1:
            self.min_length += 1
            
            self.prepare_data()
            self.predict()
            
            # orders and trades  
            if self.position == 0:
                if self.data["proba"].iloc[-1] > 0.53:
                    order = self.create_order(self.instrument, self.units, suppress = True, ret = True)
                    self.report_trade(order, "GOING LONG")
                    self.position = 1
                elif self.data["proba"].iloc[-1] < 0.47:
                    order = self.create_order(self.instrument, -self.units, suppress = True, ret = True)
                    self.report_trade(order, "GOING SHORT")
                    self.position = -1
            
            elif self.position == -1:
                if self.data["proba"].iloc[-1] > 0.53:
                    order = self.create_order(self.instrument, self.units * 2, suppress = True, ret = True)
                    self.report_trade(order, "GOING LONG")
                    self.position = 1
            
            elif self.position == 1:
                if self.data["proba"].iloc[-1] < 0.47:
                    order = self.create_order(self.instrument, -self.units * 2, suppress = True, ret = True)
                    self.report_trade(order, "GOING SHORT")
                    self.position = -1
    



