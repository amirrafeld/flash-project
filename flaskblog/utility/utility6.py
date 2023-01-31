import re
from textblob import TextBlob
import pandas as pd
import cProfile, pstats, io
import tweepy
import matplotlib.pyplot as plt
import os
twiterApi = os.environ.get('twiter_api')
apiSecretTwiter = os.environ.get('twiter3_sec_api')
token = os.environ.get('twiter_token')
token_sceret = os.environ.get('twiter_token_sec')
auto = tweepy.OAuthHandler(twiterApi, apiSecretTwiter)
auto.set_access_token(token, token_sceret)
api = tweepy.API(auto, wait_on_rate_limit=True)
plt.style.use('seaborn')



def profile(fnc):
    """A decorator that uses cProfile to profile a function"""

    def inner(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        retval = fnc(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
        return retval

    return inner


def cleantwt(twt):
    twt = re.sub('RT', '', twt)
    twt = re.sub('#[A-Za-z0-9]+', '', twt)  # remove the '#' from tweet
    twt = re.sub('\\n', '', twt)
    twt = re.sub('https?:\/\/S+', '', twt)
    twt = re.sub('@[\S]*', '', twt)
    return twt




def twitter_sentiemnt(num, stock):
    search_term = stock
    search_term.upper()
    tweets = tweepy.Cursor(api.search_tweets, q=search_term,
                           lang='en', tweet_mode='extended').items(num)
    all_tweet = [tweet.full_text for tweet in tweets]
    df = pd.DataFrame(all_tweet, columns=['tweets'])
    df['clean tweets'] = df['tweets'].apply(cleantwt)
    df = pd.DataFrame(df['clean tweets'])
    df.drop_duplicates(inplace=True)
    idx = list(range(0, len(df)))
    df = df.set_index(pd.Index(idx))
    df['subjectivity'] = df['clean tweets'].apply(getsubject)
    df['polarity'] = df['clean tweets'].apply(getpolarity)
    df['sentiment'] = df['polarity'].apply(getsentiemnt)
    plt.tight_layout()
    plt.gcf().autofmt_xdate()
    fig = plt.figure(figsize=(7, 5))
    plt.tight_layout()
    df['sentiment'].value_counts().plot(kind='bar')
    plt.title(f'Sentiemnt for {search_term}$',fontsize=12,fontname='Ariel')
    plt.ylabel(f'number of tweet {num}',fontsize=12,fontname='Ariel')
    plt.savefig(f"C:\\Users\\amirr\\Desktop\\html+css\\flask\web\\static\\matplotlib\\{search_term}.png")
    route = f'{search_term}.png'
    return route





def getsentiemnt(values):
    if values < 0:
        return 'negative'
    elif values > 0:
        return 'positive'
    else:
        return 'netural'





def getsubject(twt):
    return TextBlob(twt).sentiment.subjectivity



def getpolarity(twt):
    return TextBlob(twt).sentiment.polarity
