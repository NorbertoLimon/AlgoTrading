# Credit to Nick Mccullum and Code Academy for most of the source; condensed version for batch api calls in Python.
# Source: https://www.youtube.com/watch?v=xfzGZB4HhEE&t=5924s

import numpy as np
import pandas as pd
import requests
import math
import xlsxwriter

from secrets import SANDBOX_API_KEY

# Web Scraping the S&P 500 from Wikipedia
import urllib.request as request
from bs4 import BeautifulSoup

def getConstituents():
    # URL request, URL opener, read content
    req = request.Request('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    opener = request.urlopen(req)
    content = opener.read().decode() # Convert bytes to UTF-8

    # take the UTF-8 content and turn it into a soup
    soup = BeautifulSoup(content, features="html5lib")
    # take the soup and gather the tables
    tables = soup.find_all('table') 
    # the HTML table we actually need is tables[0]
    external_class = tables[0].findAll('a', {'class':'external text'})
    tickers = []
    for ext in external_class:
        if not 'reports' in ext:
            tickers.append(ext.string)
    return tickers

tickers = getConstituents()
ticker_array = np.array(tickers)
ticker_df = pd.DataFrame(ticker_array) # array of stock tickers
ticker_df.to_csv('sp_500_stocks.csv')

### PART 1: Single-Stock Setup ### -----------------------------------------------------------------------------------------------------------------------------------------

# Using the sandbox base url for testing
symbol = 'AAPL'
api_url = f'https://sandbox.iexapis.com/stable/stock/{symbol}/quote/?token={SANDBOX_API_KEY}'
columns = ['Ticker Symbol', 'Stock Price', 'Market Cap', '# Shares to Buy']
df = pd.DataFrame(columns=columns)
data = requests.get(api_url).json()
price = data['latestPrice']
market_cap = data['marketCap']
df.append(pd.Series([symbol, price, market_cap, 'N/A'], index=columns), ignore_index=True)
df.head()
### PART 2: LOOPING ### ----------------------------------------------------------------------------------------------------------------------------------------------------

df = pd.DataFrame(columns=columns)
for stock in ticker_df[0]:
    api_url = f'https://sandbox.iexapis.com/stable/stock/{stock}/quote/?token={SANDBOX_API_KEY}'
    stock_data = requests.get(api_url).json()
    df = df.append(pd.Series([stock, stock_data['latestPrice'], stock_data['marketCap'], 'N/A'], index=columns), ignore_index=True)

### PART 3: BATCH API CALLS ------------------------------------------------------------------------------------------------------------------------------------------------

def segments(lst, num):
    """Yields lst as segments of size num"""
    for i in range(0, len(lst), num):
        yield lst[i:i + num]

'''Prints the stock symbols inn segments of up to 100 stocks each segment'''
# List of 6 segments (lists) of length: 100, 100, 100, 100, 100, 5
symbol_groups = list(segments(ticker_df[0], 100))
# list of symbols per segment
symbol_strings = []

# for each segment:
#   100 elements are comma delimited and joined together as one string; append the 6 strings
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))
#print(symbol_strings)

final_df = pd.DataFrame(columns=columns)
for symbol_string in symbol_strings:
    batch_api_url = f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={symbol_string},fb,tsla&types=quote&token={SANDBOX_API_KEY}'
    data = requests.get(batch_api_url).json()
    for symbol in symbol_string.split(','):
        '''Parse batch api call for every symbol'''
        final_df = final_df.append(
            pd.Series(
            [
                symbol,
                data[symbol]['quote']['latestPrice'],
                data[symbol]['quote']['marketCap'],
                'N/A'
            ],
            index=columns),
            ignore_index=True
        )
final_df

len(symbol_groups) # just a sanity check

### PART 4: Calculating # Shares to Buy ### --------------------------------------------------------------------------------------------------------------------------------

portfolio_size = input('Enter the value of your portfolio: ')
flag = False
while(flag==False):
    try:
        val = float(portfolio_size)
        #vprint('Success!')
        flag=True
    except(ValueError):
        # print('Invalid input.Please specify a number value')
        portfolio_size = input('Enter the value of your portfolio: ')

# position size = how much money you are going to invest in each stock
position_size = val/len(final_df.index)

# Apple Example with a hard coded 500 price
number_of_appl_shares = position_size/500
for i in range(0, len(final_df.index)):
    final_df.loc[i, '# Shares to Buy'] = math.floor(position_size/final_df.loc[i, 'Stock Price'])
final_df

### WRITER PHASE ### -----------------------------------------------------------------------------------------------------------------------------------------------------
writer = pd.ExcelWriter('recommended_trades.xlsx', engine='xlsxwriter') # https://github.com/PyCQA/pylint/issues/3060 pylint: disable=abstract-class-instantiated
final_df.to_excel(writer, 'Recommended Trades', index=False)
background_color = '#0a0a23'
font_color = '#ffffff'

string_format = writer.book.add_format(
    {
        'font_color' : font_color,
        'bg_color' : background_color,
        'border' : 1
    }
)

dollar_format = writer.book.add_format(
    {
        'num_format' : '$0.00',
        'font_color' : font_color,
        'bg_color' : background_color,
        'border' : 1
    }
)

integer_format = writer.book.add_format(
    {
        'num_format' : '0',
        'font_color' : font_color,
        'bg_color' : background_color,
        'border' : 1
    }
)

writer.sheets['Recommended Trades'].write('A1', 'Ticker Symbol', string_format)
writer.sheets['Recommended Trades'].write('B1', 'Stock Price', dollar_format)
writer.sheets['Recommended Trades'].write('C1', 'Market Cap', dollar_format)
writer.sheets['Recommended Trades'].write('D1', '# Shares to Buy', integer_format)
column_formats = {
    'A' : ['Ticker Symbol', string_format],
    'B' : ['Stock Price', dollar_format],
    'C' : ['Market Cap', dollar_format],
    'D' : ['# Shares to Buy', integer_format]
}
for column in column_formats.keys():
    writer.sheets['Recommended Trades'].set_column(f'{column}:{column}', 18, column_formats[column][1])
    writer.sheets['Recommended Trades'].write(f'{column}1', column_formats[column][0], column_formats[column][1])
writer.save()
print('Finished!!')