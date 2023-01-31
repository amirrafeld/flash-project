import queue
import threading
#########################################################
from flask import Blueprint
from flask import redirect, render_template, request, url_for

import flaskblog.web.routes
from flaskblog.forms import (Indicators, InsiderBuy,
                        Sentiement, Twitt)
from flaskblog.models import Post
from flaskblog.utility.utilities1 import inviznews
from flaskblog.utility.utilities2 import techanical_data
from flaskblog.utility.utility4 import inside_buy, market_sentiemnt
from flaskblog.utility.utility6 import twitter_sentiemnt
###########################################################
q = queue.Queue()
thread = threading.Thread(target=inviznews, args=(q,))
thread.start()
posts = q.get()

import os
template_dir = os.path.abspath('C:\\Users\\amirr\\Desktop\\html+css\\flask\\flaskblog\\web\\templates')
main = Blueprint('main', __name__, template_folder=template_dir)
#print(help(render_template))
###################################################
@main.route("/")
@main.route("/home")
def home():
    page = request.args.get('page',1,type=int)
#    posts2 = Post.query.order_by(Post.date_posted.desc()).paginate(page=page,per_page=5)
    if posts:
        posts1 = posts
        return render_template('home.html',posts1=posts1)
        #return render_template(url_for('templates',filename='home.html'),
        #posts1=posts1,posts2=posts2)
    return render_template('home.html',
                           )

@main.route('/techanical_indicators', methods=['GET', 'POST'])
def techanical_indicators():
    form = Indicators()
    name = ''
    name1 = ''
    if form.validate_on_submit():
        if form.validate_time(period=form.time_period.data,interval=form.time_interavel.data):
            ticker1 =  form.ticker.data
            period = form.period[    form.time_period.data]
            interval1 = form.interval[ form.time_interavel.data]
            bolinger = form.bolinger_band.data
            firstavg = form.sma1.data
            rsi = form.rsi.data
            secAvg = form.sma2.data
            macd = form.macd.data
            ex_avg = form.ewm1.data
            trueRange = form.trueRange.data
            fig1 = techanical_data(ticker=ticker1, period=period, movingAverageNo1=firstavg, interval=interval1, movingAverageNo2=secAvg, exponentialMovingAverage=ex_avg, plotMacd=macd
                                   , rsi=rsi, AverageTrueRange=trueRange, bolinger_band=bolinger)
            return render_template('techanical indicators.html', title='About', fig1=fig1,form=form)
        else:
            return redirect(url_for('techanical_indicators'))

    return render_template('techanical indicators.html', title='About',form=form)
############################################################



############################################################################


@main.route("/derivative", methods=['GET', 'POST'])
def derivative():
    name = None
    name1 = None
    stock = Sentiement()
    stock = Sentiement()
    if stock.validate_on_submit():
        name = stock.stock1.data
        name1 = stock.date.data
        stock = ''
        fig1 = market_sentiemnt(stock=name,user_date=name1)
        stock = Sentiement()
        return render_template('Derivative.html', fig1=fig1, stock=stock)

    elif stock.stock1.data != "":
            if stock.is_submitted():
                name = stock.stock1.data
                stock = ' '
                fig = market_sentiemnt(name)
                stock = Sentiement()
                return render_template('Derivative.html', fig=fig, stock=stock)

    return render_template('Derivative.html', stock=stock)


@main.route('/socialMedia', methods=['POST', 'GET'])
def twiterSentiemnt():
    form = Twitt()

    if form.validate_on_submit():
        name = form.number_of_search.data
        name1 = form.search.data
        form = ''
        fig1 = twitter_sentiemnt(name,name1)
        form = Twitt()

        return render_template('socialMedia.html',fig1=fig1,form=form)

    return render_template('socialMedia.html',form=form)


@main.route("/Insider's", methods=['GET', 'POST'])
def insider():
    name = ''
    form = InsiderBuy()
    if form.validate_on_submit():
        name = form.ticker.data
        name1 = form.max_result1.data

        days = form.days_Go_dic[form.days_ago.data]
        form = ''

        fig1 = inside_buy(company=name,max_result=name1,days_go=days)
        form = InsiderBuy()

        return render_template('insiders.html',form=form,fig1=fig1)

    return render_template('insiders.html',form=form)










# Define Dash app layout

# Create Flask server
