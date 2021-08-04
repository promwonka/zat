
import pandas as pd
import numpy as np
import pickle
from datetime import datetime, timedelta
#import simplefix

class DNNTrader(simplefix.simplefix):
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

    def login_fix ():
        msg = simplefix.FixMessage()
        msg(8=FIX4.3|9=114| 35=A |34=1| 553=fx1294946| 554=123| 98=0 |108=30 |141=Y|)

        
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
    
    
        
    def on_success(self, time, bid, ask):
        print(self.ticks, end = " ")
        
        # store and resample tick data and join with historical data
        df = pd.DataFrame({self.instrument:(ask + bid)/2}, 
                          index = [pd.to_datetime(time)])
        self.tick_data = self.tick_data.append(df)
        self.resample_and_join()
        
        if len(self.raw_data) > self.min_length - 1:
            self.min_length += 1
            
            self.prepare_data()
            self.predict()
            
            # orders and trades  
            if self.trade == 'Buy':
                order = self.create_order(8=FIX.4.3  35=8 55=GBPUSD  C=input 38=1 54=2 52=20160411  1=xxxxxx )
                self.report_trade(order, "GOING LONG")

            
            elif self.trade == 'Sell':
                order = self.create_order( 8=FIX.4.3 35=8 55=GBPUSD 38=1 54=1  C=input 52=20160411  1=xxxxxx )
                self.report_trade(order, "GOING SHORT")
    



