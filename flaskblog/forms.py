from flask_wtf import FlaskForm
from flask import flash
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, SubmitField, PasswordField, BooleanField, TextAreaField,IntegerField,SelectField,DateField
from wtforms.validators import DataRequired, length, number_range, EqualTo, Length, Email, ValidationError
from flaskblog.models import User
##############################################################################################


##############################################################################

class Sentiement(FlaskForm):
    stock1 = StringField('Ticker',validators=[DataRequired()])
    date = DateField('Optional - Last dates for experations')
    submit = SubmitField('Get Data')

class Twitt(FlaskForm):
    search = StringField("term to search ",
                         validators=[DataRequired(), length(min=2)])
    number_of_search = IntegerField('number of search',
                                   validators=[DataRequired(), number_range(min=30, max=1000)])
    submit = SubmitField('search ')

###########################################################################
class Indicators(FlaskForm):
    interval = {"1 Day": '1d',"5 Day": "5d","1 Week":"1wk","1 Month": "1mo","1 Minute": "1m","15 Minute":"15m","30 Minute":"30m",'60 Minute':"60m"}
    period = {"1 Year":'1y',"1 Month":'1mo',"3 Month":'3mo',"6 Month":'6mo' ,"2 Years":'2y',"5 Years" :"5y","10 Years":'10y',"YTD" :'ytd',"MAX":'max',"1 Day":'1d',"5 Days" :"5d"}

    ticker = StringField("Ticker",
                         validators=[DataRequired(), length(min=1)])
    time_interavel = SelectField(label='Closing interval',choices=interval.keys(),validate_choice=[DataRequired()])

    time_period = SelectField(label='Starting Period',choices=period.keys(),validate_choice=[DataRequired()])

    sma1 = StringField("Moving Average No.1")
    sma2 = StringField("Moving Average No.2")
    ewm1 = StringField("Exponantional Moving Average")
    rsi = BooleanField('RSI')
    bolinger_band = BooleanField('Bolonger Bend')
    macd = BooleanField('MACD')

    trueRange= BooleanField('ATR')
    submit = SubmitField('Get Data ')
    def validate_time(self,period,interval):
       dummy_interval = ['15 Minute', '30 Minute', '60 Minute', '90m',"1 Minute"]
       dummy_period =  ['1 Year','2 Years','5 Years','10 Years','YTD','MAX']
       if period in dummy_period and interval in dummy_interval:
          flash('Interday date is only avilable for the last 60 days','danger')
       else:
           return True
class InsiderBuy(FlaskForm):
    days_Go_dic = {"4 Year": '1461',"2 Years": "730", "1 Year":"365", "6 Month": "180", "3 Month": '90', "1 Month": "30", 'All Dates':'All Dates'}
    ticker = TextAreaField('Ticker', validators=[DataRequired()])
    max_result1 = TextAreaField('Max result', validators=[DataRequired()])
    days_ago = SelectField(label='Data from',choices=days_Go_dic.keys())
    submit = SubmitField('Get Data')



class Test(FlaskForm):
    p = SubmitField('test')
    ps1 = SubmitField('tes23t')
    ps2 = SubmitField('tes23t')


