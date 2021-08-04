import streamlit as st
from stviz import viewapp
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

# c.execute("INSERT INTO userstable(username,password) VALUES ('Pramod','123kr')")
# conn.commit()

def add_userdata(username,password):
	c.execute("INSERT INTO userstable(username,password) VALUES ('%s','%s')"%(username,password))
	conn.commit()

def login_user(username,password):
	c.execute("SELECT * FROM userstable WHERE username ='%s' AND password = '%s'"%(username,password))
	data = c.fetchone()
	return data

def vizapp():
    st.title("Forex Trader")

    menu = ["Login","Signup (Temporarily Disabled)"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice  == "Login":

        username  = st.sidebar.text_input("User Name")
        password  = st.sidebar.text_input("Password", type  = 'password')
        if st.sidebar.checkbox("Login"):

            result  = login_user(username, password)
            if result:
                st.success("Logged in as {}".format(username))
                task = st.selectbox("Select Insights", ["EUR-USD","GBP-USD"])
                if task == "EUR-USD":
                    viewapp('eurusd')
                if task == "GBP-USD":
                    st.subheader("No Data to visualize, ' {} ' is not being traded as of now".format(task))                    

            else:
               st.warning("Incorrect Password / Username")

    elif choice == "Signup (Temporarily Disabled)":
        st.subheader("No Access")





if __name__ == '__main__':
    vizapp()
