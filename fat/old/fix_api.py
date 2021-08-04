from datetime import datetime, timedelta
import simplefix
import uuid

# 8, 34, 35, 49, 52, and 56
# BEGIN_STRING = "8=FIX.4.3"
# STR_SEQ = ["49=dev", "56=uat.FXS"]
# message.append_string(BEGIN_STRING, header=True)
# append_buffer()
# get_message()
# get()
# count()


def login_fix ():

    try:
        now = datetime.now()
        message = simplefix.FixMessage()
        message.append_pair(8, "FIX.4.3")
        message.append_pair(9, 99)
        message.append_pair(35, "A")
        message.append_pair(34,1)
        message.append_pair(49, "dev")
        message.append_pair(52, now)
        message.append_pair(56, "uat.FXS")
        message.append_pair(98, 0)
        message.append_pair(108, 30)
        message.append_pair(141, "Y")
        message.append_pair(553, "fxtuat")
        message.append_pair(554, "uat")
        message.append_pair(10, 14)
        
    except Exception as e:
        print(e)
    else: 
        byte_buffer = message.encode()
        print(byte_buffer.get_message())
        return 'successfully logged in'
    finally:
        print('end of function login_fx' )


def heartbeat_fn():

    try:
        now = datetime.now()
        message = simplefix.FixMessage()
        message.append_pair(8, "FIX.4.3")
        message.append_pair(9, 99)
        message.append_pair(35, "A")
        message.append_pair(34,1)
        message.append_pair(49, "dev")
        message.append_pair(52, now)
        message.append_pair(56, "uat.FXS")
        message.append_pair(112, 1)
        message.append_pair(10, 14)

    except Exception as e:
        print(e)
    else: 
        byte_buffer = message.encode()
        print(byte_buffer.get_message())
        return 'heartbeat working'
    finally:
        print('end of function heartbeat' )


def logout_fix ():

    try:
        now = datetime.now()
        message = simplefix.FixMessage()
        message.append_pair(8, "FIX.4.3")
        message.append_pair(9, 99)
        message.append_pair(35, 5)
        message.append_pair(34,1)
        message.append_pair(49, "dev")
        message.append_pair(52, now)
        message.append_pair(56, "uat.FXS")
        message.append_pair(10, 14)
    except Exception as e:
        print(e)
    else: 
        byte_buffer = message.encode()
        print(byte_buffer.get_message())
        return 'successfully logged out'
    finally:
        print('end of function logout_fix' )



# def holdings():

#     try:
#         now = datetime.now()
#         message = simplefix.FixMessage()
#         message.append_pair(8, "FIX.4.3")
#         message.append_pair(9, 99)
#         message.append_pair(35, "A")
#         message.append_pair(34,1)
#         message.append_pair(49, "dev")
#         message.append_pair(52, now)
#         message.append_pair(56, "uat.FXS")
#         message.append_pair(10, 14)
#     except Exception as e:
#         print(e)
#     else:
#         byte_buffer = message.encode()
#         print(byte_buffer.get_message())
#         return 'successfully fetched holdings'
#     finally:
#         print('end of function holdings' )
    
unique_id = uuid.uuid1()
def create_buy_order(lt_sz,amount):

    try:
        now = datetime.now()
        message = simplefix.FixMessage()
        message.append_pair(8, "FIX.4.3")
        message.append_pair(9, 99)
        message.append_pair(35, "A")
        message.append_pair(34,1)
        message.append_pair(49, "dev")
        message.append_pair(52, now)
        message.append_pair(56, "uat.FXS")
        message.append_pair(11, unique_id)
        message.append_pair(55,"EURUSD" )
        message.append_pair(54, 1)
        message.append_pair(60, now)
        message.append_pair(38, 1)
        message.append_pair(40, 1)
        message.append_pair(21, 1)
        message.append_pair(10, 14)
    except Exception as e:
        print(e)
    else: 
        byte_buffer = message.encode()
        print(byte_buffer.get_message())
        return 'successfully created buy order', unique_id
    finally:
        print('end of function create_buy_order' )

def create_sell_order(lt_sz,amount):

    try:
        now = datetime.now()
        message = simplefix.FixMessage()
        message.append_pair(8, "FIX.4.3")
        message.append_pair(9, 99)
        message.append_pair(35, "A")
        message.append_pair(34,1)
        message.append_pair(49, "dev")
        message.append_pair(52, now)
        message.append_pair(56, "uat.FXS")
        message.append_pair(11,unique_id )
        message.append_pair(55, "EURUSD" )
        message.append_pair(60, now)
        message.append_pair(54, 2)
        message.append_pair(38, 1)
        message.append_pair(40, 1)
        message.append_pair(21, 1)
        message.append_pair(10, 14)
    except Exception as e:
        print(e)
    else: 
        byte_buffer = message.encode()
        print(byte_buffer.get_message())
        return 'successfully created sell order', unique_id
    finally:
        print('end of function create_sell_order' )

unique_id2 = uuid.uuid1()
def execution_report(lt_sz,amount):

    try:
        now = datetime.now()
        message = simplefix.FixMessage()
        message.append_pair(8, "FIX.4.3")
        message.append_pair(9, 99)
        message.append_pair(35, "A")
        message.append_pair(34,1)
        message.append_pair(49, "dev")
        message.append_pair(52, now)
        message.append_pair(56, "uat.FXS")
        message.append_pair(37,unique_id )
        message.append_pair(17,unique_id2 )
        message.append_pair(150,8 )
        message.append_pair(39,8 )
        message.append_pair(55, "EURUSD" )
        message.append_pair(60, now)
        message.append_pair(54, 1)
        message.append_pair(38, 1)
        message.append_pair(40, 1)
        message.append_pair(21, 1)
        message.append_pair(10, 14)
    except Exception as e:
        print(e)
    else: 
        byte_buffer = message.encode()
        print(byte_buffer.get_message())
        return 'successfully created sell order', unique_id
    finally:
        print('end of function create_sell_order' )









# python3 -c 'import fix_api; print (fix_api.login_fix())'