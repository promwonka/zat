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




# ---------------------------------- DROP TABLE--------------------------------------------------

# c.execute("""DROP TABLE data;
#             """)
# conn.commit()

# c.execute("""ALTER TABLE data DROP COLUMN IF EXISTS d_id""")
# conn.commit()
#----------------------------------------------------------
c.execute("""CREATE TABLE IF NOT EXISTS data (
            d_id SERIAL NOT NULL,
            utc time,
            askprice float,
            bidprice float,
            askvolume float,
            bidvolume float,
            currency text                     
            )""")
conn.commit()

#HOLDING



c.execute("""CREATE TABLE IF NOT EXISTS HOLDING (
            h_id SERIAL NOT NULL PRIMARY KEY,
            avg_price float,
            total_amount float,
            lot_size float,
            currency text,
            status boolean          
            )""")
conn.commit()


# WAITLIST

c.execute("""CREATE TABLE IF NOT EXISTS WAITLIST (
            w_id SERIAL PRIMARY KEY ,
            type text,
            amount float,
            lot_size float,
            currency text,
            data_time time,
            place_time time,
            status boolean          
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
            status boolean          
            )""")
conn.commit()



# #DATA

# c.execute("""CREATE TABLE IF NOT EXISTS DATA (
#             d_id integer NOT NULL PRIMARY KEY,
#             name text,
#             amount float,
#             av_amt float,
#             currency text,
#             status boolean          
#             )""")
# conn.commit()




conn.close()




# pgadmin user name = pramodcoris@gmail.com
# passwrd = sameaspc