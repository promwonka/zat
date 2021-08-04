import getopt, sys
import pandas as pd
 
arg_list = sys.argv[1:]

print('reading first dataset')
df1 = pd.read_csv(arg_list[0],parse_dates = ["UTC"], index_col = "UTC")
df1 = df1[:300000]
df1['currency'] = arg_list[1]

print('reading second dataset')
df2 = pd.read_csv(arg_list[2],parse_dates = ["UTC"], index_col = "UTC")
df2 = df2[:300000]
df2['currency'] = arg_list[3]

print('concatinating datasets')
df3 = pd.concat([df1, df2])
# df3["UTC"] = pd.to_datetime(df3["UTC"])
df3.to_csv('currency_data_%s.csv'%arg_list[4])

print('done')