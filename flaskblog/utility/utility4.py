import concurrent.futures
import time
from plotly.subplots import make_subplots
import plotly.offline
import datetime
from datetime import timedelta, datetime
import pandas as pd
import numpy as np
import yfinance as yf
import warnings
from threading import Thread
import plotly.graph_objects as go
from flaskblog.utility.utility3 import get_marketCap, CustomThread, get_option, download, share_float, logo_update
from flaskblog.utility.utility5 import short_sala_data,loop_fig
from time import perf_counter
warnings.simplefilter(action='ignore', category=Warning)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.reset_option('all')

def get_value(x):
    return x

def inside_buy(company='COIN', max_result=1000,days_go=''):

    start = perf_counter()
    company = company
    max_result = max_result
    days1_go = f'http://openinsider.com/screener?s={company}&o=&pl=&ph=&ll=&lh=&fd={days_go}&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&xs=1&vl=&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt={max_result}&page=1'

    url = f"http://openinsider.com/screener?s={company}&o=&pl=&ph=&ll=&lh=&fd=0&fdr=&td=730&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&xs=1&vl=&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt={max_result}&page=1"

    if days_go != "All Dates":
        df = pd.DataFrame(pd.read_html(days1_go)[11])
    else:
        df = pd.DataFrame(pd.read_html(url)[11])



    df = pd.DataFrame(pd.read_html(url)[11])
    df.transpose()
    df.columns = ['X', 'Filing_Date', 'Trade_Date', 'Ticker', 'Insider Name', 'Title',
                  'Trade_Type', 'Price', 'Qty', 'Owned', 'ΔOwn', 'Value', '1d', '1w',
                  '1m', '6m']

    df['Sale_or_buy'] = df['Trade_Type'].apply(lambda x: 0 if 'S - Sale' in x else 1)
    try:
        df["Trade_Date"] = df['Trade_Date'].apply(lambda x: datetime.strptime(x, "%Y-%m-%d"))
    except:
        df["Trade_Date"] = df['Trade_Date'].apply(lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S"))

    df['Trade_Date_Plus'] = df['Trade_Date'] + timedelta(days=60)
    df["Trade_Date"] = df['Trade_Date'].apply(lambda x: x.strftime("%Y-%m-%d"))
    df["Trade_Date_Plus"] = df['Trade_Date_Plus'].apply(lambda x: x.strftime("%Y-%m-%d"))
    df = df[['Sale_or_buy', 'Trade_Date', 'Ticker', 'Value', 'Trade_Date_Plus']]
    df.rename(columns={'Trade_Date': 'Date'}, inplace=True)

    df['Date'] = pd.to_datetime(df['Date'])

    today = datetime.now().strftime('%Y-%m-%d')
    df4 = yf.download(company, start=df['Date'].iloc[-1], end=today)
    df7 = pd.DataFrame(df4)
    df7.reset_index(inplace=True)
    df7['Date'] = df7['Date'].apply(lambda x: x.strftime('%Y-%m-%d'))
    df7['Date'] = pd.to_datetime(df7['Date'])
    df8 = pd.merge(df7, df, how='left', on='Date')


    df9 = df8.copy()
    filter_buy = np.where(df9.Sale_or_buy == 1.0)
    filter_sale = np.where(df9.Sale_or_buy == 0)

    df9['Value'] = df9['Value'].apply(lambda x: x if isinstance(x, float) else x[2:])
    df9['Value'] = df9['Value'].apply(lambda x: x if isinstance(x, float) else int(x.replace(",", '')))
    df9.set_index('Date', inplace=True)
    size_buy = df9['Value'].iloc[filter_buy]
    size_sale = df9['Value'].iloc[filter_sale]

    setSizeBuy1 = pd.DataFrame(size_buy.sort_values())
    setSizeSale1 = pd.DataFrame(size_sale.sort_values())

    setSizeBuy1.reset_index(inplace=True)
    setSizeSale1.reset_index(inplace=True)
    df9.reset_index(inplace=True)
    setSizeBuy = pd.merge(setSizeBuy1.copy(), df9, how='inner', on='Date')
    setSizeSale = setSizeSale1.copy().merge(df7, on='Date')

    y0 = df8['Adj Close'].min()

    fig = go.Figure()

    procesSell = Thread(target=loop_fig, kwargs=({'fig':fig, 'df':setSizeSale, 'x':setSizeSale['Date'],
                                               'y':setSizeSale['Adj Close'], 'y0':y0, 'name': 'Inside Sale',
                                               'ColorIncremnt':1}))

    procesBuy = Thread(target=loop_fig,
                       args=(fig, setSizeBuy, setSizeBuy.Date, (setSizeBuy['Adj Close']), y0, 'InsideBuy', 2
                             ))

    procesSell.start()
    procesBuy.start()

    fig.add_trace(go.Scatter(x=df8['Date'][1:], y=df8['Adj Close'][1:], y0=y0, line=dict(color='#021B79', width=2),
                             showlegend=False))





    fig.update_layout(legend_tracegroupgap=4)
    fig.update_layout(title=company.upper(),  font=dict(size=19, color="#ffffff", family="sans-serif"))
    fig.update_yaxes(tickfont=dict(family='sans-sarif', color='#ffffff', size=14), linewidth=2, linecolor='#ffffff')
    fig.update_xaxes(tickfont=dict(family='sans-sarif', color='#ffffff', size=14), linewidth=2, linecolor='#ffffff')
    fig.update_layout(margin=dict(l=10, r=2, t=3, b=2), xaxis_rangeslider_visible=False)
    fig.update_layout(legend_tracegroupgap=15)
    fig.update_layout({'plot_bgcolor': 'rgba(0,0,0,0)', 'paper_bgcolor': 'rgba(0,0,0,0)'}, height=700, width=1400,
                      autosize=False)
    plot_div = plotly.offline.plot(fig, output_type='div')
    end = perf_counter()
    procesSell.join()
    procesBuy.join()
    total = end - start
    fig.show()
    return plot_div

from concurrent.futures import ThreadPoolExecutor

def market_sentiemnt(stock, user_date=None):
    fig = make_subplots(rows=1, cols=3, specs=[[{"type": "pie"}, {"type": "pie"}, {'type': 'pie'}]],
                        horizontal_spacing=0.08)
    start = time.time()
    SevenYearsAgo = datetime.now() - timedelta(days=(365 * 7))
    SevenYearsAgo = SevenYearsAgo.strftime('%Y-%m-%d')
    ###################################################################################################
 #    thread5 = CustomThread(target=logo_update, args=(stock, fig, 1.07,))
 #    thread1 = CustomThread(target=get_option, args=(stock, user_date))
 #    thread2 = CustomThread(target=short_sala_data, args=(stock,))
 #    thread3 = CustomThread(target=download, args=(stock, SevenYearsAgo,))
 #    thread4 = CustomThread(target=get_marketCap, args=(stock,))
 #    thread6 = CustomThread(target=share_float, args=(stock,))
 #    thread1.start()
 #    thread2.start()
 #    thread3.start()
 #    thread4.start()
 #    thread5.start()
 #    thread6.start()
 # ####################################################################################################################
 #    stockVol = thread3.join()
 #    shortDf, allData = thread2.join()
 #    ShortedStock, ShareFolat, RecordDate = thread6.join()
 #    puts, calls, expireDate = thread1.join()
 #    companyName, marketCap, fiftyTwoWeeksLow, fiftyTwoWeeksHigh, currency, exchange = thread4.join()
 #

    with concurrent.futures.ProcessPoolExecutor() as executor:
        f1 = executor.submit(logo_update,stock, fig, 1.0)
        f2 = executor.submit(get_option,stock, user_date)
        f3 = executor.submit(short_sala_data, stock)
        f4 = executor.submit(download,stock)
        f5 = executor.submit(get_marketCap,stock)
        f6 = executor.submit(share_float,stock)



        stockVol = f4.result()
        #print(stockVol)
        pool1 = time.time()
        print(f'pool1 {pool1-start}')
        #print(f3.result())
        shortDf, allData = f3.result()
        pool2 = time.time()
        print(f'pool2 {pool2-start}')

        #ShortedStock, ShareFolat, RecordDate = f6.get()
        pool3 = time.time()
        print(f'pool3 {pool3-start}')

        puts, calls, expireDate = f2.result()

        pool4 = time.time()
        print(f'pool4 {pool4-start}')

        companyName, marketCap, fiftyTwoWeeksLow, fiftyTwoWeeksHigh, currency, exchange = f5.result()
        pool5 = time.time()
        print(f'pool5 {pool5-start}')


    ###########################################################################################
    secondTime = time.time()
    print(f'finish therad {secondTime-start} second')
    if shortDf is not False:
        if allData != '2':
            print(allData)
            ShortedStock = shortDf['short'].iloc[-1]
            last_month_short = shortDf['short'].iloc[-3]
            lastMonthFloat = allData['Share Float'][-3]

            ShareFolat = allData['Share Float'][-1]
        else:
            ShortedStock = shortDf['Short Interst'][-1]
            last_month_short = shortDf['Short Interst'][-3]
            ShareFolat = shortDf['Share Float'][-1]
            lastMonthFloat = shortDf['Share Float'][-3]

    avgVol_30 = stockVol['Volume'].rolling(30).mean()
    lastAvgVol = avgVol_30[-1]
    LastMonthVol = avgVol_30[-2]
    #####################################################3333################

    PutsSum = puts['Volume'].sum()
    CallsSum = calls['Volume'].sum()
    PutCallRatio = PutsSum / CallsSum
    PutCallRatio = f"{round(PutCallRatio, 2)}%"


    #calls_ration = f"{round(CallsSum / (PutsSum + CallsSum) * 100), 2}%"
    #puts_ratio = f"{round(PutsSum / (PutsSum + CallsSum), 2) * 100}%"
    putsLabel = 'Puts'
    callsLabel = 'Calls'


    putCallArray = np.array([CallsSum, PutsSum])
    putCallLabel = [callsLabel, putsLabel]
    putCallColor = ['rgb(8,57,46)', 'rgb(164,4,3)']


    #######################################################################################################
    SI = (round((ShortedStock / ShareFolat), 5) * 100)
    SILastMonth = (round((last_month_short / lastMonthFloat), 5) * 100)
    SiMoM = round((SI / SILastMonth), 2)
    SIMoMLabel = f'{round((SiMoM - 1), 2)}% MoM'
    SI_array = np.array([ShortedStock, ShareFolat])
    SIPieLabel = ['Short', 'Long']
    SI_color = ['rgb(218,164,92)', 'rgb(59,68,131)']
    SILabel = f"Short Intertst as % of the float - {SI}%"
    if (SiMoM - 1) <= 1:
        siColor = 'rgb(8,57,46)'
    else:
        siColor = 'rgb(164,4,3)'

    ##############################################################

    SIR = round((ShortedStock / lastAvgVol), 2)
    SIRLastMonth = round((last_month_short / LastMonthVol), 1)
    SIRMoMLabel = f'{round(((SIR / SIRLastMonth) - 1), 2)}% MoM'
    if ((SIR / SIRLastMonth) - 1) <= 0:
        colorChange = 'rgb(164,4,3)'

    else:
        colorChange = 'rgb(8,57,46)'

    lastDates = stockVol.index[-1].strftime("%B %d, %Y")
    sirArray = np.array([ShortedStock, lastAvgVol])
    sirColor = ['rgb(81,135,165)', 'rgb(167,129,56)']
    sirPieLabel = ['Shorted Stock', '30 Day Avg Volume']

    sirLabel = f" Short Interst Ratio - {SIR} - Days to cover as of {lastDates}"
    thirdTime = time.time()
    print(f'third time {thirdTime -start} sec')


    fig.add_trace(go.Pie(values=sirArray, labels=sirPieLabel, textinfo='label+percent', insidetextorientation='radial',
                         marker=dict(colors=sirColor), name='Short Covorage', showlegend=False), row=1, col=1)

    fig.add_trace(go.Pie(values=SI_array, labels=SIPieLabel, textinfo='label+percent',
                         insidetextorientation='radial', marker=dict(colors=SI_color), name='Short Ratio',
                         showlegend=False), row=1, col=2)

    fig.add_trace(go.Pie(values=putCallArray, labels=putCallLabel, textinfo='label+percent',
                         insidetextorientation='radial', marker=dict(colors=putCallColor), name='PUT & CALL RATIO',
                         showlegend=False), row=1, col=3)

    fig.data[0].domain = {'x': [0.1, 0.3], 'y': [0.25, 0.75]}
    fig.data[1].domain = {'x': [0.40, 0.6], 'y': [0.25, 0.75]}
    fig.data[2].domain = {'x': [0.7, 0.9], 'y': [0.25, 0.75]}

    MarketCapLabel = f'Market Cap : {marketCap}'

    fiftyTwoWeekRang = f'Fifty Two Weeks Rang {round(fiftyTwoWeeksHigh), 1} {round(fiftyTwoWeeksLow), 1}{currency}'
    exchange = f'Exchange: {exchange}'

    fig.update_layout(
        title_text=companyName,
        annotations=[
            dict(text=f'PUT CALL RATIO - {PutCallRatio} - Last Date for expeiration-  {expireDate}', x=0.94, y=0.8,
                 font=dict(size=16, color="white", family="sans-serif"),
                 align="center", showarrow=False),
            dict(text=f'{SILabel}', x=0.5, y=0.8, font=dict(size=16, color="white", family="sans-serif"),
                 align="center", showarrow=False),

            dict(text=f' {sirLabel} ', x=0.05, y=0.8,
                 font=dict(size=16, color="white", family="sans-serif")
                 , align="center"
                 , showarrow=False),
            dict(text=SIRMoMLabel, x=0.19, y=0.5, font=dict(color=colorChange, family='sans-serif', size=11),
                 align='center', showarrow=False),
            dict(text=SIMoMLabel, x=0.5, y=0.5, font=dict(color=siColor, family='sans-serif', size=11),
                 align='center', showarrow=False),
            dict(text=MarketCapLabel, align='left', showarrow=False, x=0.19, y=0.95, xref='paper', yref='paper',
                 font=dict(size=18, color='white', family="sans-serif"), bordercolor='grey', height=20.5,
                 borderwidth=1.1),
            dict(text=fiftyTwoWeekRang, align='left', showarrow=False, x=0.5, y=0.95, xref='paper', yref='paper',
                 font=dict(size=18, color='white', family="sans-serif"),
                 borderwidth=1.1,
                 height=20.5),

            dict(text=exchange, align='left', showarrow=False, x=0., y=0.986, xref='paper', yref='paper',
                 font=dict(size=15, color='white', family="sans-serif"))])


    fourtTime = time.time()
    print(f'four time {fourtTime-start} sec')

    fig.update_traces(hole=.7)
    fig.update_layout(margin=dict(l=0, r=0, t=55, b=0))
    fig.show()
    fig.update_layout({'plot_bgcolor': 'rgba(0,0,0,0)','paper_bgcolor': 'rgba(0,0,0,0)'}, height=800, width=1620)

    fig.update_layout(
        font_family="sans-seri",
        font_color="#ffffff",
        title_font_family="sans-seri",
        title_font_color="#ffffff",
        font_size=16,
        legend_title_font_color="#ffffff")
   # thread5.join()

    #fig.update_layout({'plot_bgcolor': 'black'})
    fig.show()

    plot_div = plotly.offline.plot(fig, output_type='div')
    end = time.time()
    print((f'{end-start} finish in sec'))

    return plot_div


if __name__ == '__main__':
    market_sentiemnt('NVDA')
