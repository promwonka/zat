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

c.execute("DROP SEQUENCE IF EXISTS serial seq_id_gen_buy")
conn.commit()

c.execute("CREATE SEQUENCE seq_id_gen_buy START 1000000 INCREMENT 1 MINVALUE 1000000 ") 
conn.commit()

c.execute("CREATE SEQUENCE seq_id_gen_sell START 5000000 INCREMENT 1 MINVALUE 1000000 ") 
conn.commit()



# from datetime import datetime
# datetime object containing current date and time
# now = datetime.now()

# c.execute("INSERT INTO waitlist VALUES ('0','Sell', 1140, 1,'eurusd','%s')" %(now))
# conn.commit()


# ---------------------------------- DROP TABLE--------------------------------------------------


#c.execute("""DELETE FROM holding;
#            """)
#conn.commit()
c.execute("""DROP TABLE tr_history;
            """)
conn.commit()

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
            crncy_qty float,
            currency text,
            t_time text,
            stime text,
            etime text,
            order_id int       
            )""")
conn.commit()


# WAITLIST

c.execute("""CREATE TABLE IF NOT EXISTS WAITLIST (
            w_id SERIAL PRIMARY KEY ,
            type text,
            amount float,
            crncy_qty float,
            currency text,
            w_time text       
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

#tr_history

c.execute("""CREATE TABLE IF NOT EXISTS tr_history(
                trid SERIAL NOT NULL PRIMARY KEY,
                type text,
                avg_price float,
                crncy_qty float, 
                currency text, 
                status text,
                executed_price float,
                executed_qty float,
                t_time text,
                stime text,
                etime text,
                order_id int)""")
conn.commit()


#Holding

c.execute("""CREATE TABLE IF NOT EXISTS holding (
            h_id SERIAL NOT NULL PRIMARY KEY,
            amount float,
            crncy_qty float,
            currency text,
            status boolean          
            )""")
conn.commit()





# UPDATE public.fund
# 	SET amount=100000, av_amt=20000, rem_amt=80000
# 	WHERE f_id = 1;

c.execute("INSERT INTO fund (f_id,name,amount, av_amt, rem_amt, currency,status, initial_amount, initial_trade_percentage) VALUES (1,'fund_one',100000,20000,80000,'eurusd',TRUE, 100000,20)")
conn.commit()


c.execute("INSERT INTO public.holding(h_id, amount, crncy_qty, currency, status) VALUES (1, 0, 0, 'eurusd', TRUE)")
conn.commit()

c.execute("INSERT INTO userstable(username, password) VALUES ('Wudi','wudieuros')")
conn.commit()


c.close()
conn.close()




# # pgadmin user name = pramodcoris@gmail.com
# # passwrd = sameaspc
# #sudo /usr/pgadmin4/bin/setup-web.sh
