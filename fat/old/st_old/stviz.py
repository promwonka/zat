import psycopg2
import streamlit as st
import pandas as pd

#connect to the db

conn = psycopg2.connect(
        host = "localhost",
        database = "corispsql_db",
        user = "corispsql",
        password = "coris@pc",
        port = 5432

)

c = conn.cursor()

def fetch_data(crr,val):
    c.execute("SELECT * FROM data  WHERE currency = '%s' ORDER BY d_id DESC LIMIT '%s' "%(crr,val))
    dt = c.fetchall()
    conn.commit()
    return dt

@st.cache
def load_data(crr):
    c.execute("SELECT * FROM tradelist  WHERE currency = '%s' "%(crr))
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


def fund_view(crr):
    c.execute("SELECT * FROM FUND WHERE currency = '%s'" %crr)
    dt = c.fetchone()
    conn.commit()
    return dt


def viewapp(crr):

    task = st.selectbox("Select Insights", ["Overview","Trades","Waitlist", "Raw Data"])
    if task == "Overview":
        overviewer(crr)
    if task == "Trades":
        trade_viewer(crr)
    if task == "Waitlist":
        waitlist_viewer(crr)
    if task == "Raw Data":
        rawdata_viewer(crr)
        
    
def overviewer(crr):
    fv = fund_view(crr)

    st.subheader('Total Amount = {} '.format(fv[7]))
    tra = ((fv[7]*fv[8])/100)
    st.subheader('Trade Amount = {}'.format(tra))
    st.write("(Trade Allocation is {} % of Total Amount)".format(fv[8]))
    st.subheader('Total Profits = {}'.format(fv[2]-fv[7]))
    

    wd = wait_data('eurusd')
    lnwd = len(wd)
    sumwd = wd['Price'].sum()

    ld = load_data('eurusd')
    lnld = len(ld)
    trtr = (lnld-lnwd)/2
    st.write('Total round transactions = ', trtr)
    

    st.write('Available trade amount = ', fv[3])
    st.write('Pending orders in Wait List = ', lnwd)
    st.write('Pending transactions in Trade List = ', lnld - trtr)
 
    st.button("Re-run")



def trade_viewer(crr):
    wd = wait_data('eurusd')
    lnwd = len(wd)
    sumwd = wd['Price'].sum()
    ld = load_data('eurusd')
    lnld = len(ld)
    trtr = (lnld-lnwd)/2
    
    st.subheader('Trade Data')
    # st.write('Total transactions = ', lnld)
    # st.write('Total round transactions = ', trtr)
    # st.write('Pending transactions in Trade List = ', lnld - trtr)
    # trade_data = load_data(crr)
    df = pd.read_csv('vzsheet.csv')
    st.write(df)
    import plotly.express as px
  
    # Loading the iris dataset
    df = pd.read_csv('vzsheet.csv')
    
    fig = px.scatter(df, x="Time2", y="Price",
                    color="Type")
    fig.show()
    st.button("Re-run")


def waitlist_viewer(crr):
    st.subheader('Waitlist Data')
    wl_data = wait_data(crr)
    st.write(wl_data)


def rawdata_viewer(crr):

    task = st.selectbox("Choose latest 'x' data points from dropdown to view", ["10 Thousand","100 Thousand","1 Million","1 ", "10 Million", "100 Million"])
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

def data_viewer(crr,val):

    st.subheader('Raw Data')
    dt = fetch_data(crr,val)
    df = pd.DataFrame(dt, columns = ['d_id', 'UTC', 'AskPrice','BidPrice','AskVolume','BidVolume','currency'])
    df['UTC'] = pd.to_datetime(df['UTC'], errors='coerce')
    df.drop(['d_id', 'currency'], axis=1, inplace = True)
    df['Price'] = (df['AskPrice'] + df['BidPrice'])/2
    df = df[['UTC','Price']].copy()
    # df['Price'] = df['Price']*10000000
    st.write(df[:12000])
    st.line_chart(df[:12000].rename(columns={'UTC':'index'}).set_index('index'))
    st.button("Re-run")


