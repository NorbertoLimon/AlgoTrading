import numpy as np
import pandas as pd
import requests
import math
import xlsxwriter

"""CELL BREAK"""

# Web Scraping the S&P 500 from Wikipedia
import urllib.request as request
from bs4 import BeautifulSoup

def getConstituents():
    # URL request, URL opener, read content
    req = request.Request('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    opener = request.urlopen(req)
    content = opener.read().decode() # Convert bytes to UTF-8

    soup = BeautifulSoup(content)
    tables = soup.find_all('table') # HTML table we actually need is tables[0]

    external_class = tables[0].findAll('a', {'class':'external text'})

    tickers = []

    for ext in external_class:
        if not 'reports' in ext:
            tickers.append(ext.string)

    return tickers

"""CELL BREAK"""
tickers = getConstituents()
ticker_array = np.array(tickers)
ticker_df = pd.DataFrame(ticker_array)

"""CELL BREAK"""
print("Hello Wurld")
#from secrets import SANDBOX_API_KEY

"""CELL BREAK"""



# Using the sandbox base url for testing
# Here you should incorporate the better versions; dont waste time or space with bs