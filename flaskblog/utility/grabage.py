
from datetime import datetime
import plotly.graph_objects as go
from datetime import timedelta
import plotly.offline

import pandas as pd
import numpy as np
import yfinance as yf

def getGradeinet(df,sale):
    xcolor1 = []
    xcolor2 = []
    xcolor3 = []

    if sale == 1:
            t = 1

            color2 = [196,65,65]
            color1= [255, 0, 0]
            color3 = [255,77,166]
            for i in range(len(df)):
                a= [color1[0] - t, color1[1], color1[2]]
                b= [color2[0]-t, color2[1]-t , color2[2]-t]
                c = [color3[0], color3[1], color3[2] - t]
                t = t + 0.7
                if a[0] <= 0:
                    a[0] = 0

                if b[1] or b[2] <0:
                    b[1] = 0
                    b[2] = 0

                if c[2] <= 0:
                    c[2] = 0
                a = tuple(a)
                b = tuple(b)
                c = tuple(c)
                xcolor1.append(a)
                xcolor3.append(c)
                xcolor2.append(b)


    else:

        t = 1
        color2 = [0, 255, 38,1]
        color1 = [0,255, 0,1]
        color3 = [38, 255, 0,1]
        for i in range(len(df)):

            a = [color1[0]  , color1[1]-t -t, color1[2]]
            b = [color2[0], color2[1] , color2[2]-t]
            c = [color3[0]-t, color3[1], color3[2]]
            t = t + 1

            print(i)
            if a[1] <= 0:
                a[1] = 0
            if b[2] < 0:
                b[2] = 0
            if c[0] <= 0:
                c[0] = 0
            a= tuple(a)
            b= tuple(b)
            c = tuple(c)

            xcolor1.append(a)
            xcolor2.append(b)
            xcolor3.append(c)

def set_pixel(df):
    pixel = 19
    empty_pixel = []
    for i in range(len(df)):

        empty_pixel.append(pixel)
        if i <  37:
            pixel =pixel + 1.4

        elif i < 45 and i > 39:
            pixel = pixel + 0.66


        elif i >45 and i < 48:
            pixel = pixel + 0.3

        elif i > 48:
            pixel = pixel + 0.005

        else:
            pixel = pixel + 0.61


    df['pixel'] = empty_pixel
    return df

def inside_buy(company, max_result, days_go=''):
    company = company
    max_result = max_result
    days1_go = f'http://openinsider.com/screener?s={company}&o=&pl=&ph=&ll=&lh=&fd={days_go}&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&xs=1&vl=&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt={max_result}&page=1'

    url = f"http://openinsider.com/screener?s={company}&o=&pl=&ph=&ll=&lh=&fd=0&fdr=&td=730&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&xs=1&vl=&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt={max_result}&page=1"

    if days_go != "All Dates":
        df = pd.DataFrame(pd.read_html(days1_go)[11])
    else:
        df = pd.DataFrame(pd.read_html(url)[11])

    ################################################################################
    df.transpose()
    df.columns = ['X', 'Filing_Date', 'Trade_Date', 'Ticker', 'Insider Name', 'Title',
                  'Trade_Type', 'Price', 'Qty', 'Owned', 'ΔOwn', 'Value', '1d', '1w',
                  '1m', '6m']

    # df = pd.DataFrame(pd.read_html(days_go)[11])

    # df.set_index('X',inplace=True)

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

    today = datetime.now().strftime('%Y-%m-%d')
    df4 = yf.download(company, start=df['Trade_Date'].iloc[-1], end=today)
    df7 = pd.DataFrame(df4)
    df7.reset_index(inplace=True)

    df7['Date'] = df7['Date'].apply(lambda x: x.strftime('%Y-%m-%d'))

    df8 = pd.merge(df7, df, how='left', on='Date')

    df8['Date'] = pd.to_datetime(df8['Date'], format='%Y-%m-%d')
    filter_buy = np.where(df8.Sale_or_buy == 1.0)
    filter_sale = np.where(df8.Sale_or_buy == 0)

    df8.reset_index(inplace=True)
    df9 = df8.copy()
    df9.dropna(inplace=True)
    df9.set_index('Date', inplace=True)
    df9['Value'] = df9['Value'].apply(lambda x: x[2:])
    df9['Value'] = df9['Value'].apply(lambda x: int(x.replace(",", '')))
    filter_buy = np.where(df9.Sale_or_buy == 1.0)
    filter_sale = np.where(df9.Sale_or_buy == 0)

    size_buy = df9['Value'].iloc[filter_buy]
    size_sale = df9['Value'].iloc[filter_sale]

    setSizeBuy = pd.DataFrame(size_buy.sort_values())
    setSizeSale = pd.DataFrame(size_sale.sort_values())
    setSizeSale = set_pixel(setSizeBuy)
    setSizeSale = set_pixel(setSizeSale)

    setSizeBuy.reset_index(inplace=True)
    setSizeSale.reset_index(inplace=True)
    df9.reset_index(inplace=True)
    setSizeBuy = pd.merge(setSizeBuy, df9, how='inner', on='Date')

    setSizeSale = pd.DataFrame(setSizeSale)
    df9['Date'] = pd.DatetimeIndex(df9['Date'])
    setSizeSale['Date'] = pd.DatetimeIndex(setSizeSale['Date'])
    df9.set_index('Date', inplace=True)
    setSizeSale.set_index('Date', inplace=True)

    setSizeSale = setSizeSale.join(df9['Adj Close'])
    try:
        setSizeSale.drop_duplicates(inplace=True)
    except TypeError:
        pass

    y0 = df8['Adj Close'].min()
    tn = 1
    fig = go.Figure()
    RedIncremnt = 'rgb(191,64,64)'
    GreenIncremnt = 'rgb(148,197,140)'

    print(len(setSizeSale))
    for i in range(len(setSizeSale)):
        n = go.Scatter(x=[setSizeSale.index[i]], y0=y0, y=[setSizeSale['Adj Close'][i]], mode='markers',
                       showlegend=False, name='Insider Sale', opacity=1,
                       marker=dict(size=setSizeSale['pixel'][i], gradient=dict(color=RedIncremnt,
                                                                               type="radial")),
                       line=dict(width=1.5, color=RedIncremnt))

        if tn <= (len(setSizeSale) / 4):
            RedIncremnt = 'rgb(191,64,64)'
        elif tn <= len(setSizeSale) / 3:
            RedIncremnt = 'rgba(159,55,55)'

        elif tn <= len((setSizeSale) / 2):
            RedIncremnt = 'rgba(141,52,52)'
        else:
            RedIncremnt = 'rgba(129,41,41)'

        tn = tn + 1

        fig.add_trace(n)

    tx = 1
    for i in range(len(setSizeBuy)):
        t = go.Scatter(x=[setSizeBuy.Date[i]], y0=y0, y=[setSizeBuy['Adj Close'].iloc[i]], mode='markers',
                       showlegend=False, name='Insider Sale', opacity=1,
                       marker=dict(size=setSizeBuy['pixel'][i], gradient=dict(color=GreenIncremnt,
                                                                              type="radial")),
                       line=dict(width=1.5,
                                 color=GreenIncremnt))
        if tx <= (len(setSizeBuy) / 4):
            GreenIncremnt = 'rgb(100,173,98)'
        elif tx <= len(setSizeBuy) / 3:
            GreenIncremnt = 'rgba(26,136,40)'

        elif tx <= len(setSizeBuy) / 2:
            GreenIncremnt = 'rgba(10,105,33)'
        else:
            GreenIncremnt = 'rgba(9,79,41)'
        tx = tx + 1
        fig.add_trace(t)

    fig.add_trace(go.Scatter(x=df8['Date'][1:], y=df8['Adj Close'][1:], y0=y0, line=dict(color='#021B79', width=2),
                             showlegend=False))
    fig.update_layout(legend_tracegroupgap=14)

    fig.update_layout(title=company.upper())
    fig.update_layout({'plot_bgcolor': 'rgba(0,0,0,0)', 'paper_bgcolor': 'rgba(0,0,0,0)'}, height=800, width=1960)
    fig.update_yaxes(title_text=" Close $ USD")
    fig.update_xaxes(title='Date')
    fig.update_layout(margin=dict(l=10, r=2, t=3, b=2))

    plot_div = plotly.offline.plot(fig, output_type='div')
    fig.show()

    return plot_div