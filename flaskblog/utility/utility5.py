import time

import numpy as np
import plotly.offline
from threading import Thread
from threading import Lock
import pandas as pd
from bs4 import BeautifulSoup
import re
import datetime
import warnings
import plotly.graph_objects as go
import requests
import yfinance as yf
from requests.exceptions import ConnectionError
from datetime import timedelta, datetime
from time import perf_counter
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.reset_option('all')

def loop_fig(fig, df, x, y, y0, name, ColorIncremnt):
    size = 12
    pixel = 0.01
    lock = Lock()
    lock.acquire()
    opacity = 1
    #if ColorIncremnt != 1:


    if ColorIncremnt != 1:
        first = ['#ffffff', '#90ee90', 'rgb(116,195,101)', '#50c878']
        second = ['#ffffff', 'rgb(20,119,31)', 'rgb(19,171,16)', 'rgb(36,197,55)']
        three = ['#ffffff', 'rgb(19,170,82)', 'rgb(0,102,43)', 'rgb(0,100,0)']
        four = ['#ffffff', 'rgb(24,80,44)', 'rgb(24,80,44)', 'rgb(11,47,24)']
    else:
        first = ['rgb(234,60,83)', 'rgb(235, 179, 177, 1)', 'red', 'rgb(191,10,47)']
        second = ['rgba(163,90,82)', 'rgb(235,60,83)', 'rgb(210,35,18)', 'rgb(210,31,60)']
        three = ['#ffffff', 'rgb(210,31,60)', 'rgb(126,25,27)', 'rgb(210,31,60)']
        four = ['#ffffff', 'rgb(214,33,33)', 'rgb(199,44,44)', 'rgb(184,15,10)']

#green
    #     first = ['#ffffff', '#90ee90', 'rgb(116,195,101)', '#50c878']
    #     second = ['#ffffff', 'rgb(20,119,31)', 'rgb(19,171,16)', 'rgb(36,197,55)']
    #     three = ['#ffffff', 'rgb(19,170,82)', 'rgb(0,102,43)', 'rgb(0,100,0)']
    #     four = ['#ffffff', 'rgb(24,80,44)', 'rgb(24,80,44)', 'rgb(11,47,24)']
    #
    # else: #red
    #     first = ['rgb(234,60,83)', 'rgb(235, 179, 177, 1)', 'red', 'rgb(191,10,47)']
    #     second = ['rgba(163,90,82)', 'rgb(235,60,83)', 'rgb(210,35,18)', 'rgb(210,31,60)']
    #     three = ['#ffffff', 'rgb(210,31,60)', 'rgb(126,25,27)', 'rgb(210,31,60)']
    #     four = ['#ffffff', 'rgb(214,33,33)', 'rgb(199,44,44)', 'rgb(184,15,10)']

    if pixel < 0.02:
        ColorIncremnt = first
    lock.release()

    for i in range(len(df)):
        n = go.Scatter(x=[x[i]], y=[y[i]], y0=y0, mode='markers', showlegend=False, name=name, marker=
        dict(size=size, color=ColorIncremnt[3], symbol='circle', opacity=opacity,
             gradient=dict(color=[ColorIncremnt[1], ColorIncremnt[2]], type='radial'),
             line=dict(width=1, color=ColorIncremnt[0])))


        if pixel <= (len(df) * 0.10):
            ColorIncremnt = first

            size = 16.2
            # print('number 10',pixel)
            opacity = 1

        elif pixel <= (len(df) * 0.2):
            size = 19.1
            ColorIncremnt = first

            opacity = 0.9
            # print('number 9', pixel)
        elif pixel <= (len(df) * 0.3):
            size = 21.9
            ColorIncremnt = first

            opacity = 0.8

        elif pixel <= (len(df) * 0.4):
            size = 25.85
            ColorIncremnt = second

            opacity = 0.7

        elif pixel <= (len(df) * 0.5):
            size = 29.45
            ColorIncremnt = second

            opacity = 0.6
        elif pixel <= (len(df) * 0.6):
            size = 33.43
            ColorIncremnt = second

            opacity = 0.5
        elif pixel <= (len(df) * 0.7):
            ColorIncremnt = three

            size = 36.6
            opacity = 0.51

        elif pixel <= len(df) * 0.8:
            size = 39
            ColorIncremnt = three

            opacity = 0.55
        elif pixel < (len(df) * 0.9):
            size = 50.7
            ColorIncremnt = four

            opacity = 0.58

        else:
            ColorIncremnt = four
            size = 53
            opacity = 0.55
        lock.acquire()
        pixel += 1
        lock.release()
        fig.add_trace(n)






def short_sala_data(ticker):
    try:
        start = time.time()
        print(f'start short sale data{start}')
        url = f'https://www.benzinga.com/quote/{ticker}/short-interest'
        oururl = requests.get(url, 'html.parsel')
        soup = BeautifulSoup(oururl.content, 'lxml')
        GenralList = []
        for script in soup("script"):
            GenralList.append(script.extract().text)
        extract = re.compile('{([^}]*)}')
        match = re.findall(extract, GenralList[-1])
        firstList = []
        for second in match:
            k = re.sub(pattern='"', repl='', string=second)
            firstList.append(k)

        firstStop = time.time()
        print(f'until first stop in shor_sale_data {firstStop-start} sec')
        secondList = []
        for second in firstList:
            if second.startswith("re"):
                if second not in secondList:
                    secondList.append(second)


        secondStop = time.time()
        print(f'until second stop in short sale data {secondStop-start}')
        shortPattern = re.compile(r'totalShortInterest:\d+')
        preforemnce52weekPattern = re.compile(r'performance52Wk:(\d+|-\d+|\d+.\d+|-\d+.\d+)')
        shareFloatPatter = re.compile(r'sharesFloat:\d+')
        datePattern = re.compile(r'recordDate:\d+-\d+-\d+')
        lastMonthShortPattrtn = re.compile(r'shortPriorMo:\d+')
        dailyVolPattern = re.compile(r'averageDailyVolume:\d+')
        daytoCoverPattern = re.compile(r'daysToCover:\d+.\d+')

        NumShort = re.compile(r'\d+')
        NumDate = re.compile(r'\d+-\d+-\d+')
        NumDayToCover = re.compile(r'\d+.\d+')
        NumVol = re.compile(r'\d+')
        NunLastMonthShort = re.compile('\d+')

        NumShareFloat = re.compile('\d+')
        Num52week = re.compile('(\d+|-\d+|\d+.\d+|-\d+.\d+)')
        allData = {'record Date': [], 'Short Interst': [], "Day To Cover": [], 'Avg Daily Vol': [], "last Month Short": [],
                   'Share Float': [], '52Weeks': []}


        for i in range(len(secondList)):
            shortInterst = re.findall(pattern=shortPattern, string=secondList[i])
            recordDate = re.findall(pattern=datePattern, string=secondList[i])
            dayToCover = re.findall(pattern=daytoCoverPattern, string=secondList[i])
            avgDailyVol = re.findall(pattern=dailyVolPattern, string=secondList[i])
            lastMonthShort = re.findall(pattern=lastMonthShortPattrtn, string=secondList[i])
            Preforemnce52Weeks = re.findall(pattern=preforemnce52weekPattern, string=secondList[i])
            ShareFloat = re.findall(pattern=shareFloatPatter, string=secondList[i])

            try:
                record = re.findall(pattern=NumDate, string=recordDate[0])
                #if str(record[0])  not in allData['record Date']:

                short = re.findall(pattern=NumShort, string=shortInterst[0])
                allData['Short Interst'].append(int(short[0]))


                day_to_cover = re.findall(pattern=NumDayToCover, string=dayToCover[0])

                allData['Day To Cover'].append(float(day_to_cover[0]))

                avgDay = re.findall(pattern=NumVol, string=avgDailyVol[0])
                allData['Avg Daily Vol'].append(str(avgDay[0]))


                lastshort = re.findall(pattern=NunLastMonthShort, string=lastMonthShort[0])
                allData['last Month Short'].append(int(lastshort[0]))

                try:
                    share = re.findall(pattern=NumShareFloat, string=ShareFloat[-1])
                except TypeError:
                    share = re.findall(pattern=NumShareFloat, string=ShareFloat[0])

                last52 = re.findall(pattern=Num52week, string=Preforemnce52Weeks[0])

                allData['52Weeks'].append(f'{int(last52[0])} %')
                allData['Share Float'].append(int(share[0]))



            except IndexError:
                pass
        thirdStop = time.time()
        print(f'until third stop in short sale func {thirdStop-start}')
        df = pd.DataFrame()
        try:
            df = pd.DataFrame(allData)


        except ValueError:

            try:
                df = pd.DataFrame({'record': allData['record Date'], 'short': allData['Short Interst'],
                                   'day to cove': allData['Day To Cover'], 'last month': allData['last Month Short']})
            except ValueError:
                try:
                    df = pd.DataFrame({'record': allData['record Date'], 'short': allData['Short Interst'],
                                       'day to cover': allData['Day To Cover']})
                except ValueError:
                    try:
                        df = pd.DataFrame({'record': allData['record Date'], 'short': allData['Short Interst']})

                        df1 =  pd.DataFrame({'day to cove': allData['Day To Cover'], 'last month': allData['last Month Short'],"Share Floats":[]})
                    except:
                        pass

        end = time.time()
        print(f'inish short sale data in {end-start}')
        if not df.empty:
            print('return 1')
            return df,allData
        else:
            print('return two')
            return allData,'2'




    except ConnectionError:
        return False


if __name__  == '__main__':
    short_sala_data('NVDA')










