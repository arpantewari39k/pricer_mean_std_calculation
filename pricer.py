import getopt
import math
import sys
import time
import traceback

import pandas as pd
import numpy as np
import requests


import requests


usage = f"""\n\tUsage: python finding_numbers_binance.py -s <Symbol> -r <resample freq> -t <number of trades>\n\n"""

# try:
#     opts, args = getopt.getopt(sys.argv[1:], "s:r:t:h", ["symbol=", "resample=", "trades=", "help"])
# except getopt.GetoptError:
#     print(f"\nInvalid arguments\n{usage}")
#     sys.exit(2)

# symbol, resample, trades = None, None, None

# if len(opts) == 0:
#     print(f"\nNo arguments\n{usage}")
#     sys.exit(2)

# for opt, arg in opts:
#     if opt == '-h':
#         print(usage)
#         sys.exit(0)
#     elif opt in ("-s", "--symbol"):
#         symbol = arg.upper()
#     elif opt in ("-r", "--resample"):
#         resample = arg
#     elif opt in ("-t", "--trades"):
#         arg = int(arg)
#         if arg > 500:
#             tmp = math.floor(arg/500)
#             trades = [500] * tmp
#             trades.append(arg - (500 * tmp))
#         else:
#             trades = [arg]
market = 'BTCUSDT'
symbol ='BTCUSDT'
resample = '1m'
trades=1
if symbol == None or resample == None or trades == None:
    print(f"\nIncomplete arguments\n{usage}")
    sys.exit(2)

frame = pd.DataFrame()
market = 'BTCUSDT'
tick_interval = '8h'

base_url = 'https://api.binance.com/api/v3/klines?symbol='+market+'&interval='+resample
#base_url = f"https://www.deribit.com/api/v2/public/get_last_trades_by_instrument?sorting=default&instrument_name={symbol}"
end_seq = None
print("\n-----> Downloading data...\n")
trades =['BTCUSDT','ETHUSDT','BUSDUSDT','SOLUSDT','FILUSDT']
list_di=[]
print(trades)
for index in range(len(trades)):
    try:
        if index == 0:
            url = f"{base_url}&count={trades[index]}"
        elif end_seq:
            url = f"{base_url}&count={trades[index]}&end_seq={end_seq}"
        #print(url)
        base_url = 'https://api.binance.com/api/v3/klines?symbol='+trades[index]+'&interval='+resample
        print(base_url)
        response = requests.get(base_url, headers={'Content-Type': 'application/json'}).json()
        data=pd.DataFrame(response)
        data.columns = ['open_time','open', 'high', 'low', 'close', 'amount','close_time', 'qav','num_trades','taker_base_vol','taker_quote_vol', 'ignore']
        data.index = [pd.to_datetime(x, unit='ms').strftime('%Y-%m-%d %H:%M:%S') for x in data.open_time]
        usecols=['open', 'high', 'low', 'close', 'amount']
        data = data[usecols]
        print(data.head())
        data = data.astype('float')
        frame=data.copy()
        frame.index=pd.to_datetime(frame.index)
        xxx=frame.copy()
        xxx['amount'] = abs(xxx['amount'])
        xxx['value'] = xxx['amount']*xxx['close']
        xxx = xxx.resample('1s').sum()
        xxx = xxx.drop(xxx[xxx['amount']<=0].index,axis=0)
        xxx = xxx.drop(xxx[xxx['value']<=10].index,axis=0)
        xxx['logs'] = np.log(xxx['amount'])
        standard_deviation = math.sqrt(((xxx['logs'] - xxx['logs'].mean())**2).sum()/(len(xxx['logs']) - 1))
        mean_sd_dict = {'market' : trades[index], 'mean' : xxx['logs'].mean(), 'std' : standard_deviation}
        print(mean_sd_dict)
        list_di.append(mean_sd_dict)

  
        #frame = pd.concat([frame, pd.DataFrame(response['result']['trades'])])
        # if len(trades) > 1:
        #     end_seq = response['result']['trades'][-1]['trade_seq']
        #     time.sleep(0.5)
    except:
        traceback.print_exc()
        print(response.json())
df=pd.DataFrame(list_di)
print(df)