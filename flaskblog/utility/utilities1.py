from http.client import IncompleteRead, RemoteDisconnected

import time
from urllib.error import URLError
import re
from time import sleep
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup


def inviznews(q):
    while (True):
        try:
            url1 = 'https://finviz.com/news.ashx'

            updates = []

            req = Request(
                url=url1,
                headers={'User-Agent': 'Mozilla/5.0'})
            webpage = urlopen(req).read()

            data = webpage.decode('UTF-8')
            soup = BeautifulSoup(data, 'html.parser')
            headers = []
            time12 = []

            last = soup.find_all('tr', class_='nn')
            for i in last:
                update = i.find_all('a')
                for i in update:
                    header = i.text
                    headers.append(header)
            for n in last:
                dates = n.find_all('td', class_='nn-date')
                for n in dates:
                    date = n.text
                    time12.append(date)
            k = []
            patern = r"[0-9]{2}:[0-9]{2}[AP][M]"
            com = re.compile(patern)
            l = dict(zip(time12, headers))
            time1 = []
            head = []
            for key, values in l.items():

                if [key] == com.findall(key):
                    time1.append(key)
                    head.append(values)

            complite1 = dict(zip(time1, head))
            post = {}
            b = 0
            for key, val in complite1.items():
                if b < 10:
                    post[key] = val
                    b = b + 1
            q.put(post)


        except URLError:
            q.put("NO INTERNET CONECTION")
        except IncompleteRead:
            q.put("Problem with site")
            time.sleep(5*60)
        except RemoteDisconnected:
            time.sleep(1*60)
        sleep(20)



if __name__=='__main__':
    pass











