import psycopg2
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
from db_connect import db_conn_fn

#connect to the db

conn = db_conn_fn()
c = conn.cursor()

def fetch_data(crr,val):
    c.execute("SELECT * FROM data  WHERE currency = '%s' ORDER BY d_id DESC LIMIT '%s' "%(crr,val))
    dt = c.fetchall()
    return dt


def data_viewer(crr,val):

    st.subheader('Raw Data')
    dt = fetch_data(crr,val)
    df = pd.DataFrame(dt, columns = ['d_id', 'UTC', 'AskPrice','BidPrice','AskVolume','BidVolume','currency'])
    df['UTC'] = pd.to_datetime(df['UTC'], errors='coerce')
    df.drop(['d_id', 'currency'], axis=1, inplace = True)
    df['Price'] = (df['AskPrice'] + df['BidPrice'])/2

    dtall = load_tr_data(crr)
    dt = dtall[dtall['Status'] == 'Success']
    dt = dt[['t_time','Type','Executed price','Executed Qty']]
    dt = dt.rename(columns={'t_time':'UTC'})
    dt['UTC'] = pd.to_datetime(dt['UTC'], errors='coerce')
    result = df.append(dt)
    result = result.sort_values('UTC')
    result.reset_index(drop=True)
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=result['UTC'], y=result['Price'],
                    mode='markers',
                    name='raw'))
    fig.add_trace(go.Scatter(result, x=result['UTC'], y=result['Executed price'],
                    mode='markers', name='markers'))

    st.plotly_chart(fig)

    # st.write('Raw Data Linechart')
    # plot2 = px.line(df, x = 'UTC', y = 'Price', title = 'time vs Midprice', hover_data=['AskPrice','BidPrice','AskVolume','BidVolume'])
    # st.plotly_chart(plot2)
    st.write(df)
    # st.line_chart(df[:12000].rename(columns={'UTC':'index'}).set_index('index'))
    st.button("Re-run")

def rawdata_viewer(crr):

    task = st.selectbox("Choose latest 'x' data points from dropdown to view", ["5 Thousand","10 Thousand","100 Thousand","1 Million","1 ", "10 Million", "100 Million"])
    if task == "5 Thousand":
        data_viewer(crr,5000)
    if task == "10 Thousand":
        data_viewer(crr,10000)
    if task == "100 Thousand":
        data_viewer(crr,100000)
    if task == "1 Million":
        data_viewer(crr,1000000)
    if task == "10 Million":
        data_viewer(crr,10000000)
    if task == "100 Million":
        data_viewer(crr,100000000)


def load_tr_data(crr):
    c.execute("SELECT * FROM tr_history  WHERE currency = '%s'"%(crr))
    dt = c.fetchall()
    conn.commit()
    data = pd.DataFrame(dt, columns = ['ID', 'Type', 'Price','Currency Qty','Currency','Status','Executed price','Executed Qty','t_time','stime','etime','order id'])
    return data

def load_tradelist_data(crr):
    c.execute("SELECT * FROM tradelist  WHERE currency = '%s'"%(crr))
    dt = c.fetchall()
    conn.commit()
    data = pd.DataFrame(dt, columns = ['ID', 'Type', 'Price','Currency Qty','Currency','t_time','stime','etime','order id'])
    return data



def fund_view(crr):
    c.execute("SELECT * FROM FUND WHERE currency = '%s'" %crr)
    dt = c.fetchone()
    conn.commit()
    return dt

def overviewer(crr):
    fv = fund_view(crr)

    st.subheader('Total Amount = {} '.format(fv[7]))
    tra = ((fv[7]*fv[8])/100)
    st.subheader('Allocated Trade Amount = {}'.format(tra))
    st.write("(Trade Allocation is {} % of Total Amount)".format(fv[8]))
    dtall = load_tr_data(crr)
    dt = dtall[dtall['Status'] == 'Success']
    dtby = dt[dt['Type']=='Buy']
    dtsl = dt[dt['Type']=='Sell']


    dtsl['tot'] = dtsl['Executed price']*dtsl['Executed Qty']
    dtby['tot'] = dtby['Executed price']*dtby['Executed Qty']

    dtbysum = dtby['tot'].sum()
    dtslsum = dtsl['tot'].sum()

    TPf = (dtslsum - dtbysum)
    st.write('Total Profits = ', TPf)

    bln = len(dtby)
    sln = len(dtsl)

    st.write('Total Buy transactions = ', bln) 
    st.write('Total Sell transactions = ', sln) 
    st.write('Available trade amount = ', fv[3])
    st.button("Re-run")

def trade_viewer(crr):
    dtall = load_tr_data(crr)
    dt = dtall[dtall['Status'] == 'Success']
    dtby = dt[dt['Type']=='Buy']
    bln = len(dtby)

    dtsl = dt[dt['Type']=='Sell']
    sln = len(dtsl)

    st.write('Tradelist Scatterplot')
    dftest = load_tradelist_data(crr)
    st.write(dftest)
    plot = px.scatter(dftest, x = 't_time', y = 'Price', color = 'Type', hover_data=['stime','etime','order id','Currency Qty'])
    st.plotly_chart(plot)

    st.write('Actual Trade Scatterplot')
    plot2 = px.scatter(dt, x = 't_time', y = 'Price', color = 'Type', hover_data=['stime','etime','order id','Currency Qty','Executed price','Executed Qty'])
    st.plotly_chart(plot2)

    st.write('Total Buy transactions = ', bln) 
    st.write('Total Sell transactions = ', sln) 
    st.write(dtall)
    

def viewapp(crr):

    task = st.selectbox("Select Insights", ["Overview","Trades", "Raw Data"])
    if task == "Overview":
        overviewer(crr)
    if task == "Trades":
        trade_viewer(crr)
    if task == "Raw Data":
        rawdata_viewer(crr)
        
    


