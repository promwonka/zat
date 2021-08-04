import psycopg2

#connect to the db

conn = psycopg2.connect(
        host = "localhost",
        database = "corispsql_db",
        user = "corispsql",
        password = "coris@pc",
        port = 5432

)

c = conn.cursor()



# from datetime import datetime
# datetime object containing current date and time
# now = datetime.now()

# c.execute("INSERT INTO waitlist VALUES ('0','Sell', 1140, 1,'eurusd','%s')" %(now))
# conn.commit()


# ---------------------------------- DROP TABLE--------------------------------------------------


#c.execute("""DELETE FROM holding;
#            """)
#conn.commit()


c.execute("""DROP TABLE fund;
            """)
conn.commit()

c.execute("""DROP TABLE holding;
            """)
conn.commit()

c.execute("""DROP TABLE tradelist;
            """)
conn.commit()

c.execute("""DROP TABLE waitlist;
            """)
conn.commit()



# # c.execute("""ALTER TABLE data DROP COLUMN IF EXISTS d_id""")
# # conn.commit()
# #----------------------------------------------------------

c.execute("""CREATE TABLE IF NOT EXISTS userstable(
        username TEXT,
        password TEXT)""")

conn.commit()


c.execute("""CREATE TABLE IF NOT EXISTS data (
            d_id SERIAL NOT NULL,
            utc text,
            askprice float,
            bidprice float,
            askvolume float,
            bidvolume float,
            currency text                     
            )""")
conn.commit()

#tradelist



c.execute("""CREATE TABLE IF NOT EXISTS TRADELIST (
            t_id SERIAL NOT NULL PRIMARY KEY,
            type text,
            avg_price float,
            lot_size float,
            currency text,
            t_time time          
            )""")
conn.commit()


# WAITLIST

c.execute("""CREATE TABLE IF NOT EXISTS WAITLIST (
            w_id SERIAL PRIMARY KEY ,
            type text,
            amount float,
            lot_size float,
            currency text,
            w_time time       
            )""")
conn.commit()


#FUND

c.execute("""CREATE TABLE IF NOT EXISTS FUND (
            f_id SERIAL NOT NULL PRIMARY KEY,
            name text,
            amount float,
            av_amt float,
            rem_amt float,
            currency text,
            status boolean,
            initial_amount float,
            initial_trade_percentage float         
            )""")
conn.commit()



#Holding

c.execute("""CREATE TABLE IF NOT EXISTS holding (
            h_id SERIAL NOT NULL PRIMARY KEY,
            amount float,
            lot_size float,
            currency text,
            status boolean          
            )""")
conn.commit()


# UPDATE public.fund
# 	SET amount=100000, av_amt=20000, rem_amt=80000
# 	WHERE f_id = 1;

c.execute("INSERT INTO fund (f_id,name,amount, av_amt, rem_amt, currency,status, initial_amount, initial_trade_percentage) VALUES (1,'fund_one',100000,20000,80000,'eurusd',TRUE, 100000,20)")
conn.commit()


c.execute("INSERT INTO public.holding(h_id, amount, lot_size, currency, status) VALUES (1, 0, 0, 'eurusd', TRUE)")
conn.commit()


conn.close()




# # pgadmin user name = pramodcoris@gmail.com
# # passwrd = sameaspc
# #sudo /usr/pgadmin4/bin/setup-web.sh
