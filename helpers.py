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

def segments(lst, num):
    """Yields lst in segments of size num"""
    for i in range(0, len(lst), num):
        yield lst[i:i + num]