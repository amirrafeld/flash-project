import time
import pandas as pd
from datetime import  datetime
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from yahoo_fin import options
from threading import Thread
import base64
import requests
import yfinance as yf
import os

poliApiKey = os.environ.get('poliApi')

class CustomThread(Thread):
    def __int__(self, group=None, target=None, name=None, args=(), kwargs={}, Verbose=None):
        Thread.__init__(self=self, group=group, target=target, name=name, args=args, kwargs=kwargs)
        self._return = None
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self):
        Thread.join(self)
        return self._return

def download(stock):
    startTime = time.time()
    print(f'start download {startTime}')
    try:
        df = yf.download(stock,start='2016-01-01')
        endTime = time.time()
        print(f"finish download func in {endTime-startTime}")

        return df
    except:
        df = yf.download(stock, start='2016-01-01')
        return df


def share_float(stock):
    start = time.time()
    print(f"start share float {start}")
    url = f"https://shortsqueeze.com/?symbol={stock}"
    df1 = pd.DataFrame()
    df = pd.read_html(url)
    for i in df:
        df3 = pd.concat([df1, i])
    df3.columns = ['key', 'value']
    df3.set_index('key', inplace=True)
    firstStop = time.time()
    print(f"share_float first stop {firstStop-start}")

    try:
        days_to_cover = df3.loc['Short Interest Ratio (Days To Cover)']
    except:
        days_to_cover = 'NO DATA'

    shorted_stock = int(df3.loc['Short Interest (Current Shares Short)'])

    try:
        Shares_Float = int(df3.loc['Shares Float'])
    except ValueError:
        Shares_Float = get_float(stock)

    Record_Date = df3.loc['Record Date']
    end = time.time()
    print(f"finish share float in {end-start}")

    return shorted_stock,Shares_Float,Record_Date


def get_float(stock):
    empty = []
    url = f'https://www.floatchecker.com/stock?float={stock}'
    req = requests.get(url)
    soup = BeautifulSoup(req.content,'html.parser')
    div = soup.find_all('div', class_="wp-block-column")
    for i in div:
        li = i.find_all('li')
        for t in li:
            try:
                a = t.find('a').text
                if a != '' or a != "(Learn More)":
                    empty.append(a)
            except:
                pass
    clean_list = [x.replace('(Learn More)','') for x in empty]
    clean_list = [x.replace('B',('000000000')) for x in clean_list]
    clean_list = [x.replace('%',('')) for x in clean_list]
    clean_list = [x.replace('.',('')) for x in clean_list]
    clean_list = [x.replace('Mil',('000000')) for x in clean_list]
    clean_list = [x for x in clean_list if x !=' ']
    clean_list = [x for x in clean_list if x != '']
    share_float= clean_list[0]
    share_float = float(share_float)
    return share_float



def _get_image(path):
    with open(path, 'rb') as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    encoded_img = f'data:image/png;base64,{encoded_string}'
    return encoded_img



def get_marketCap(Tic):

    start = time.time()
    print(f"start market cap {start}")
    url = f'https://api.polygon.io/v3/reference/tickers/{Tic}?apiKey={poliApiKey}'
    req = requests.get(url)

    stockInfo = req.json()['results']
    companyName = stockInfo['name']
    currencyName = stockInfo['currency_name']
    exchange = stockInfo['primary_exchange']
    outhStandingShare = stockInfo['share_class_shares_outstanding']
    secondStop = time.time()
    print(f'second Stop in get market cop {secondStop-start} sec')

    stockData= yf.download(Tic)
    lastPrice = stockData['Adj Close'][-1]


    fiftyTwoWeeksLow = stockData['Adj Close'].iloc[-365:].values.min()
    fiftyTwoWeeksHigh  =stockData['Adj Close'].iloc[-365:].values.max()

    marketCap = round((int(outhStandingShare) * lastPrice))

    marketCap =str(marketCap)

    if len(marketCap) > 9:
        marketCap = f'{marketCap[0:-9]}.{marketCap[1]}B'

    elif (len(marketCap) <=9) and (len(marketCap) > 6):
        marketCap = f'{marketCap[0:-6]}.{marketCap[2]}M'
    else:
        marketCap = marketCap
    end = time.time()
    print(f"finish get market cap in {end-start}")

    return companyName,marketCap,fiftyTwoWeeksLow,fiftyTwoWeeksHigh,currencyName,exchange



def get_option(stock,user_date):

    start = time.time()
    if user_date == None:
        user_date = datetime.now().strftime("%Y:-%m-%d")
    stock = stock.upper()

    reqStart = time.time()
    options_date = options.get_expiration_dates(stock)
    expire_date = options_date[-1]
    two = time.time()
    print(f'sec part get option {two-start} sec')
    print(reqStart-two,' finish rec')


    if user_date != datetime.now().strftime("%Y:-%m-%d"):
        x = [datetime.strptime(i, '%B %d, %Y').date() for i in options_date]
        filter_date = [i for i in x if i <= user_date]
        convert_date = [datetime.strftime(i, '%B %d, %Y') for i in filter_date]
        expire_date = user_date
        puts = pd.DataFrame()
        calls = pd.DataFrame()
        for i in convert_date:
            try:
                ThreadCall = CustomThread(target=options.get_calls,args=(stock, i))
                ThreadPuts = CustomThread(target=options.get_puts,args=(stock, i))
                ThreadCall.start()
                ThreadPuts.start()
                put = ThreadPuts.join()
                call =ThreadCall.join()

                puts = puts.append(put, ignore_index=True)
                calls = calls.append(call, ignore_index=True)
            except:
                pass


    else:

        startReq = time.time()
        threadCalls = CustomThread(target=options.get_calls, args=(stock,))
        threadPuts = CustomThread(target=options.get_puts, args=(stock,))
        threadPuts.start()
        threadCalls.start()
        calls = threadCalls.join()
        puts = threadPuts.join()
        finishReq = time.time()
        print(f'finish req in {finishReq-startReq}')

    three = time.time()
    print(f'part three {three-start} sec')

    calls['Volume'] = calls['Volume'].apply(lambda x:float(x.replace('-', '0')))
    puts['Volume'] = puts['Volume'].apply(lambda x: float(x.replace('-', '0')))

    finish = time.time()
    print(f'finish in {finish-start}')
    return puts, calls, expire_date






    df['rgb1'] = xcolor1
    df['rgb2'] = xcolor2
    df['rgb3'] = xcolor3
    end = time.time()
    print(f' option func finish in {end-stat} sec')

    return df

def logo_update(stock,fig,n):
    start = time.time()
    url = f'https://api.polygon.io/v3/reference/tickers/{stock}?apiKey={poliApiKey}'
    req = requests.get(url)
    stockInfo = req.json()['results']


    logo_url =stockInfo['branding']['icon_url']
    logo_url = f'{logo_url}?apiKey={poliApiKey}'
    a = HTMLSession()
    cur_dir = "C:\\Users\\amirr\\Desktop\\html+css\\flask\\web\\static\\icons"
    output = cur_dir + f"/{stock}"
    if not os.path.exists(output):
        os.mkdir(output)
    req = a.get(logo_url)
    content = req.html.find('img')
    with open(output + '/' + stock + '.jpeg', 'wb') as file:
        r = a.get(logo_url)
        file.write(r.content)
    stock_logo = f"C:\\Users\\amirr\\Desktop\\html+css\\flask\\web\\static\\icons\\{stock}\\{stock}.jpeg"
    fig.update_layout(margin=dict(l=0, r=0, t=55, b=0))
    try:
        fig.add_layout_image(
            dict(
                source=_get_image(stock_logo),
                xref='paper', yref='paper',
                x=0, y=n,
                xanchor="left",

                yanchor="top",
                sizex=0.071, sizey=0.071, ))
    except:
        pass
    end = time.time()
    print(f'logo finish in {end-start}')



if __name__ == '__main__':
    get_option('AMD',None)
    #logo_update('AAPL')
    #download('NVDA',start='2020-01-02')
    #get_marketCap('NVDA')


#f'https://api.polygon.io/v1/reference/company-branding/d3d3LmFwcGxlLmNvbQ/images/2023-01-01_icon.jpeg?apiKey={poliApiKey}'