from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import yfinance as yf
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from threading import Thread
from flaskblog.utility.utility3 import CustomThread
from flaskblog.utility.utility4 import logo_update
from pandas_ta import volatility
from flaskblog.utility.utilities2 import bolonger_bond,subplot_macd
import ta

def update_dash_layout(dashLayout):
    dashLayout.layout = dbc.Container([
        dbc.Row([
            dbc.Col([

                dbc.Label("Ticker", width="auto", className='pe-1'),
                dbc.Col(
                    dbc.Input(id='stockInput', debounce=True,type='text', value='stock',placeholder="Enter Ticker"),
                    className="col-8 col-lg-4 p-3",
                ),
                dbc.Col(dbc.Button("Submit",id='submitButton', outline=True, color="secondary", className="me-1",style={'margin-top':'14px'}),width='3',className='col-2'),

            ],class_name='row row-cols-6 ml-auto'),

            dbc.Col([
                html.Div(id='graph-container', style={'display': 'none'},
                         children=[
                                  dcc.Graph(id='live-graph', animate=True),
                                  dcc.Interval(
                                      id='graph-update',
                                      interval=1 * 67000)
                             ]
                         )
            ],
                className='col-6 mr-1')

        ]),


        html.Div(
            [
                dbc.RadioItems(
                    id="date",
                    className="btn-group btn-group p-0 m-0",
                    inputClassName="btn-check ",

                    labelClassName="btn btn-intline-secondary p-0 m-0"
                                  ,
                    labelCheckedClassName="active  ",
                    options=[
                        {"label": "1 Day", "value": '1d'},
                        {"label": "5 Days", "value": '5d'},
                        {"label": "6 Month", "value": '6mo'},
                        {"label": "YTD", "value": 'ytd'},
                        {"label": "1 Year", "value": '1y'},
                        {"label": "5 Years", "value": '5y'},
                        {"label": "10 Years", "value": '10y'},
                        {"label": "MAX ", "value": 'max'},

                    ],
                    value=1, style={'font-size':'8px', 'padding': '0', 'width': '23px', 'margin': '0'},
                ),
            ], className='radio-group p-0 mt-6 ', style={'width': '140px','font-size':'8px','margin-bottom':'200px'}
        ),

],
        className='m-0 container-fluid')




def techanical_data(
        n_clicks,ticker,refresh,
        period='1d',
            movingAverageNo1='', movingAverageNo2='',
                    exponentialMovingAverage='', interval='1m', rsi=False, AverageTrueRange=False, bolinger_band=False, plotMacd=False):
    if n_clicks:
        ticker = ticker.upper()
        thread1 = CustomThread(target=yf.download,kwargs=({'tickers':ticker, 'period':period, 'interval':interval}))
        thread1.start()

        if (rsi or AverageTrueRange) and plotMacd:
            spac = [[{"type": "xy", 'secondary_y': True}], [{'type': 'xy', 'secondary_y': True}],[{'type': 'xy', 'secondary_y': True}],[{'type': 'xy', 'secondary_y': True}]]
            columns_width = [0.5,0.2,0.15,1,0.15]
            rowHeights = [0.50,0.2, 0.15, 0.15]
            rowTitle = [None, None,None ,None]
            numberOfRows = 4
            verticalSpacing = 0.07
            columnTitles = [None,None, None, None]
            n = False
        elif (plotMacd == True) and not (rsi or AverageTrueRange):
            spac = [[{"type": "xy", 'secondary_y': True}], [{'type': 'xy', 'secondary_y': True}],
                    [{'type': 'xy', 'secondary_y': True}]]
            columns_width = [0.32, 0.43, 0.16]
            rowHeights = [0.50, 0.3, 0.2]
            rowTitle = [None, None, None]
            numberOfRows = 3
            verticalSpacing = 0.02
            columnTitles = [ None, None, None]
            n = False

        elif (rsi==True) or (AverageTrueRange == True) or (plotMacd == True):
            columns_width = [0.8,0.2]
            rowHeights = [0.8, 0.2]
            rowTitle = [None, None]
            numberOfRows = 2
            verticalSpacing = 0.05
            spac = [[{"type": "xy", 'secondary_y': True}], [{'type': 'xy', 'secondary_y': True}]]
            columnTitles = [None, None]
            n =False
        else:
            rowHeights = [1]
            rowTitle = [None]
            numberOfRows = 1
            verticalSpacing = 0
            spac = [[{"type": "xy", 'secondary_y': True}]]
            columnTitles = [None]
            n= True
            columns_width = [1]

        startXline = 34 if plotMacd else 0

        fig = make_subplots(rows=numberOfRows, cols=1,shared_xaxes=True, row_heights=rowHeights, specs=spac,
                             column_titles=columnTitles,
                             row_titles=rowTitle
                             , vertical_spacing=verticalSpacing)
        thread2 = Thread(target=logo_update,args=(ticker,fig,1.06))
        thread2.start()

        df = thread1.join()


        y0= df['Adj Close'].min()

        if (rsi ^ AverageTrueRange) or (rsi & AverageTrueRange):
            fig.update_layout(xaxis_rangeslider_visible=n)

        else:
            fig.update_layout(xaxis_rangeslider_visible=n)

        fig.add_trace(go.Candlestick(x=df.index[startXline:],yaxis='y',
            open=df['Open'],whiskerwidth=1,
            high=df['High'],
            low=df['Low'],
            close=df['Adj Close'],showlegend=False),row=1,col=1)

        fig.add_trace(go.Bar(x=df.index[startXline:], width=0.76,y=df['Volume'][startXline:],yaxis='y1',opacity=0.5, orientation='h',
                              name="Volume", showlegend=False, marker=dict(color='#E0E0E0',line=dict(width=0.5,color='#E0E0E0'),)),secondary_y=True,row=1,col=1)




        if movingAverageNo1:
            movingAverageNo1 = int(movingAverageNo1)
            df[f'{movingAverageNo1}ma'] = df['Adj Close'].rolling(movingAverageNo1).mean()
            fig.add_trace(go.Scatter(x=df.index[startXline:], y0=y0,
                                     y=df[f"{movingAverageNo1}ma"][startXline:],yaxis="y1", showlegend=True,line=dict(color='rgb(185,75,63)',width=1.5), name=f"{movingAverageNo1}  Moving Average"), row=1, col=1)
        if movingAverageNo2:
            movingAverageNo2 = int(movingAverageNo2)
            df[f'{movingAverageNo2}ma'] = df['Adj Close'].rolling(movingAverageNo2).mean()
            fig.add_trace(go.Scatter(x=df.index[startXline:], y0=y0,
                                     y=df[f"{movingAverageNo2}ma"][startXline:],
                                     yaxis="y1", showlegend=True,
                                     line=dict(color='rgb(126,100,25)',
                                                width=1.5), name=f"{movingAverageNo2} Moving Average"), row=1, col=1)

        if exponentialMovingAverage:
            exponentialMovingAverage = int(exponentialMovingAverage)
            df[f'EMA{exponentialMovingAverage}'] = df['Adj Close'].ewm(span=exponentialMovingAverage, adjust=False).mean()
            fig.add_trace(go.Scatter(x=df.index[startXline:],
                                     y=df[f"EMA{exponentialMovingAverage}"][startXline:], y0=y0,
                                     line = dict(color='rgb(55,71,81)',
                                                  width=1.5), name=f"{exponentialMovingAverage} Exponant Moving Average"))


        if rsi == True:
            df['RSI'] =  ta.rsi(df['Adj Close'] , timeperiod = 14)
            fig.add_trace(go.Scatter(x=df.index[startXline:],showlegend=True,legendgroup=2,
                                      y=df["RSI"][startXline:],name=f"RSI",line=dict(color='rgb(35,93,119)',width=1.5)),secondary_y=False,row=2,col=1)


            fig.add_hline(y=30, line_width=1, line_dash="dash", line_color="rgb(81,135,165)", row=2, col=1)
            fig.add_hline(y=70, line_width=1, line_dash="dash", line_color="rgb(227,179,132)", row=2, col=1)

            fig.update_yaxes(title_text="RSI", row=2, col=1, secondary_y=False)

        if AverageTrueRange == True:
            n = True if rsi else False
            df['trueRange'] = volatility.average_true_range(df['High'],df['Low'],df['Adj Close'])
            fig.add_trace(go.Scatter(x=df.index[startXline:],y=df['trueRange'][startXline:],name='AVerage True Range',line=dict(color='#eb4d5c',
                                                                                                                                       width=1.5)),row=2,col=1,secondary_y=n)

            fig.update_yaxes(title_text='ATR', row=2, col=1, secondary_y=n)


        if plotMacd :
            subplot_macd(fig=fig, data=df,start_scatter=startXline)



        if bolinger_band:
            startXline = 15 if plotMacd else 0
            bolonger_bond(df,fig,start_scatter=startXline)


        stright = ['O', str(round(df['Open'].iloc[-1],1)),
                   'H', str(round(df['High'].iloc[-1],1)),
                   'L', str(round(df['Low'].iloc[-1],1)),
                   'C', str(round(df['Adj Close'].iloc[-1],1))]


        if df['Adj Close'].iloc[-1] >= df['Open'].iloc[-1]:
            colorcode = '#53b987'
        else:
            colorcode = '#eb4d5c'

        colors = [
            '#e4e4e4', colorcode,
            '#e4e4e4', colorcode,
            '#e4e4e4', colorcode,
            '#e4e4e4', colorcode]

        Yshift  = df['Adj Close'].max() +35 if (rsi or AverageTrueRange) else df['Close'].max() + 32
        x = 0.62 if (rsi or AverageTrueRange) else 0.61
        for s, c in zip(stright, colors):
            fig.add_annotation(dict(text=s,bgcolor=c),font_size=16,opacity=1,x=x,y=Yshift,xref="x domain",yref='y',axref='x domain',ayref='y',ax=x,ay=Yshift)
            x = x + 0.04


        interDayInterval = ['1m', '2m', '15m', '30m', '60m', '90m']

        if interval in interDayInterval:
            fig.update_layout({'plot_bgcolor': 'rgba(0,0,0,0)','paper_bgcolor': 'rgba(0,0,0,0)'},height=700, width=1760,
                               xaxis_rangebreaks=[dict(bounds=['16.00', '9.00'],pattern="hour"),
                                                  dict(bounds=['sat', "mon"])])
        else:
            fig.update_layout({'plot_bgcolor': 'rgba(0,0,0,0)','paper_bgcolor': 'rgba(0,0,0,0)'}, height=700, width=1760,
                               xaxis_rangebreaks=[dict(bounds=['sat', "mon"])])



        fig.update_layout(legend_tracegroupgap=4)
        fig.update_layout(title=ticker.upper())
        fig.update_yaxes(tickfont=dict(family='sans-sarif', color='#ffffff', size=14), linewidth=2, linecolor='#ffffff')
        fig.update_xaxes(tickfont=dict(family='sans-sarif', color='#ffffff', size=14), linewidth=2, linecolor='#ffffff')
        fig.update_yaxes(title_text='Volume',row=1,col=1,secondary_y=True)

        fig.update_yaxes(title_text="Close", row=1, col=1,secondary_y=False)

        fig.update_yaxes(title='Volume', visible=True, showticklabels=True,secondary_y=True,row=1,col=1)


        fig.update_xaxes(showgrid=False, zeroline=True)
        fig.update_yaxes(showgrid=False, zeroline=True,secondary_y=True,anchor='x1')
        fig.update_yaxes(showgrid=False, zeroline=True)

        fig.update_layout(margin=dict(l=3, r=3, t=30, b=3), yaxis_rangebreaks=[dict(bounds=['16.00', '9.00'],pattern="hour"),
                                                                                   dict(bounds=['sat', "mon"])])

        fig.update_layout(font_family="sans-seri",font_color="#ffffff",
            title_font_family="sans-seri",title_font_color="#ffffff",font_size =16,legend_title_font_color="#ffffff")
        fig.update_layout(title= {'text': ticker,'font_color':'#ffffff','y': 1.02,'x': 0.05,'xanchor': 'center','yanchor': 'top'})


        thread2.join()


        #fig.show()


        return fig




















