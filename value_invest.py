from src.stock_lookup import *
from src.get_financials_v2 import Financials
import random

# stocks = stock_lookup('Best canadian reits')
# stocks = all_stocks(sample_amt=20)
stocks = ['sis.to', 'byl.to', 'lte.v']
# stocks = ['TSLA', 'OGIG', 'NYSE', 'GARP', 'AMZN.TO', 'EPS', 'IPO.TO', 'MSFT', 'ARKF', 'YOY', 'IWB', 'ARKW', 'DIS', 'JNJ', 'IWD', 'AAPL', 'KO']
# stocks = ['rei-un.to', 'dir-un.to', 'car-un.to', 'ap-un.to', 'grt-un.to', 'chp-un.to', 'hr-un.to', 'sru-un.to', 'fcr-un.to']
print('Gathering info on stocks...')
f = Financials(stocks)
print(f.value_screener())
