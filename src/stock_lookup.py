import requests
import re
import random
from bs4 import BeautifulSoup


def stock_lookup(response):
    print(f'Searching for "{response}"...')

    try:
        buzzword = response.replace(' ', '+')
        results = 5
        page = requests.get(f"https://www.google.com/search?q={buzzword}&num={results}")
        soup = BeautifulSoup(page.content, "html.parser")

        links = soup.findAll("a")
        url_list = []
        for link in links:
            link_href = link.get('href')
            if "url?q=" in link_href and not "webcache" in link_href:
                url_list.append(link.get('href').split("?q=")[1].split("&sa=U")[0])

        url_list = url_list
        stock_list = []
        for url in url_list:
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content, 'html.parser')

                def get_tickers(text):
                    s_list = []
                    tickers = re.findall(r'[(][A-Z][\S]*[)]', text)
                    if tickers:
                        for t in tickers:
                            t = t.replace('(', '').replace(')', '')
                            if t.isupper():
                                blacklist = ['/', '&']
                                if not any(x in t for x in blacklist):
                                    s_list.append(t)

                    return s_list

                t = [get_tickers(p.text) for p in soup.find_all('p')]
                flat_t = [item for sublist in t for item in sublist]
                stock_list.append(flat_t)
            except:
                pass

        def split_ticker(ticker):
            if ':' in ticker:
                return ticker.split(':')[1]
            else:
                return ticker

        stock_list = [item for sublist in stock_list for item in sublist]
        return [split_ticker(x) for x in set(stock_list) if x]

    except:
        pass

# def get_stock_name(symbol):
#     try:
#         page = requests.get(f'https://ca.finance.yahoo.com/quote/{symbol}/key-statistics?p={symbol}')
#         soup = BeautifulSoup(page.content, 'html.parser')
#         return soup.find('h1').text
#     except:
#         return False

# def get_recommended_stocks(response):
#     stocks = stock_lookup(response)
#     stock_list = []
#     for s in stocks:
#         try:
#             s_to = s + '.TO'
#             stock_name = get_stock_name(s_to)
#             if stock_name is not False:
#                 stock_list.append(s_to)
#             else:
#                 stock_list.append(s)
#         # american
#         except:
#             stock_name = get_stock_name(s)
#             stock_list.append(stock_name)
#             pass
#     return stock_list
#
# def all_stocks(sample_amt=20):
#     with open('stock_names.txt', 'r') as f:
#         stocks = random.sample(f.read().split(', '), sample_amt)
#
#     stock_list = []
#     for s in stocks:
#         try:
#             # canadian
#             try:
#                 s = s + '.TO'
#                 stock_name = get_stock_name(s)
#                 stock_list.append(s)
#             # american
#             except:
#                 stock_name = get_stock_name(s)
#                 stock_list.append(s)
#         except:
#             pass
#     return stock_list