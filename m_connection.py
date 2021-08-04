# from kiteconnect import KiteConnect
# import pandas as pd

# api_key = "f8ikwv384iqsz4e2"
# api_secret = "467aatmlht4n4l760e8rza6x9bcm0a62"
# kite = KiteConnect(api_key = api_key)
# print(kite.login_url())

# request_token = "request_token"
# kite = KiteConnect(api_key = api_key)
# print(kite.login_url())


# request_token = "tbzAfkTQUvWZUD3R7ANl04Gv0xodCpI8"
# data = kite.generate_session(request_token, api_secret = api_secret)
# kite.set_access_token(data["access_token"])
# print(data["access_token"])
# instrument_dump = kite.instruments("NSE")
# instrument_df = pd.DataFrame(instrument_dump)
# instrument_df.to_csv("NSE_Instruments.csv", index = False)


# from selenium import webdriver
# from webdriver_manager.firefox import GeckoDriverManager

# driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
# driver.get('http://seleniumhq.org/')


from selenium import webdriver
browser = webdriver.Chrome('/home/coris/Documents/kite/chromedriver')
browser.get('http://seleniumhq.org/')

