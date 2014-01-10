#!/usr/bin/env python2.7
#encoding=utf-8

import urllib
import urllib2
import cookielib
import json
import ConfigParser

from bs4 import BeautifulSoup

from utils import *

null = "null"
true = "true"
false = "false"

class Shaybay:
    HOST = 'http://www.shanbay.com'

    def __init__(self, config_file):
        self.cookiejar = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar),urllib2.HTTPHandler(debuglevel = 0))
        self.opener.addheaders = [('User-agent','Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)')]
        self.opener.addheaders = [('content-type','application/json')]
        self.opener.addheaders.append(('Connection','keep-alive'))
        #urllib2.install_opener(opener)
        self.init_params = self.read_config(config_file)
        
    def print_cookies(self):
        for cookie in cookiejar:
            print cookie.name
            print cookie.value
    
    def open_home(self):
        request = urllib2.Request(self.HOST)
        return self.opener.open(request).read()

    def read_config(self, config_file):
        config = ConfigParser.ConfigParser()
        config.read(config_file)
        return dict(config.items('Shanbay'))

    def post(self, url, params):
        url_data = urllib.urlencode(params)
        request = urllib2.Request(url)
        res = self.opener.open(request,url_data)
        return res

    def get(self, url, params = {}):
        url += "?"
        if len(params) > 0:
            for k,v in params.items():
                url += (str(k)+"="+str(v)+"&")
            url = url[:-1]
        request = urllib2.Request(url)
        return self.opener.open(request).read()

    def put(self, url, payload):
        #url_data = urllib.urlencode(params)
        #request = urllib2.Request(url, json.dumps(payload, sort_keys=True, skipkeys=True))
        request = urllib2.Request(url, data = json.dumps(payload).replace(" ",""),headers={'Content-type':'application/json'} )
        request.get_method = lambda:'PUT'
        res = self.opener.open(request)
    
    def login(self):
        loginurl = self.HOST+'/accounts/login/'
        token = ""
        for c in self.cookiejar:
            if c.name=='csrftoken':
                token = c.value 
    
        params = self.init_params
        params["login"] = ""
        params["csrfmiddlewaretoken"] = token

        self.post(loginurl, params)
        print "Login Success"

    def word_study(self):
        #url = self.HOST + '/api/v1/bdc/review/sync/'
        url = self.HOST + '/api/v1/bdc/review/'
        
        while True:
            params = {
               #"len": 7,
               #"update_type":"fresh",
#               "index":0,
               #"_":timestamp()
            }

            res = self.get(url, params)
            ids = self.get_wordid(res)
            if len(ids) == 0:
                break
            rand_pause()
            params2 = {}
            for i in ids[0:7]:
                params2[i] = 2
            res = self.put(url, params2)

    def get_wordid(self, json):
        json = eval(json)
        ids = []
        reviews = json["data"]["reviews"]
        for r in reviews:
            ids.append(r["id"])
        
        return ids

    def reading_study(self):
        """
        step 1: open news page
        step 2: choose the first news
        step 3: open news page, turn page every 20~25s
        step 4: finish reading button
        step 5: choose the second news....
        """
        url = self.HOST + '/api/v1/read/'
        news_ids = self.get_news_id(self.HOST+'/read/news/')
        for n in news_ids:
            total_time = 0
            res = self.get(url+'article_content/'+n,{"_":timestamp()})
            data = eval(res)["data"]
            last_read_sentence = data["last_read_sentence"]
            page = data["content"]

            soup = BeautifulSoup(page)

            # if there is image at the first page
            if soup.find("img"):
                self.put(url+"article/user/"+n, {"operation":"record"})
                
            sents = soup.findAll("sent")
            print sents
            print len(sents)

            for s in sents[::4]:
                span = s.find(class_="paragraph").span
                if not span:
                    continue
                sentence_id = span['id']
                used_time = rand_pause() 
                total_time += used_time
                
                params = {
                "operation":"record",
                "sentence_id":sentence_id,
                "used_time":used_time
                }

                self.put(url+"article/user/"+n, params)

            # finish
            params = {
            "comment":"",
            "used_time":total_time,
            "operation":"finish"
            }
            self.put(url+"article/user/"+n)

    def get_news_id(self, url):
        """
        Get news id(only the newest two)
        """
        news = []
        page = self.get(url)
        soup = BeautifulSoup(page)
        articles = soup.findAll(class_="article")[0:2]
        for a in articles:
            n = a.find(class_="title").a["href"]
            print "news -->",n
            news.append(n.strip('/').split('/')[-1])

        return news

    def checkin(self):
        url = self.HOST+'/api/v1/checkin/?for_web=true'
        headers = {
        "Content-Type":"application/json"
        }
    
        request = urllib2.Request(url)
        response = self.opener.open(request)
        payload = eval(response.read())
        print "num_checkin_days:",payload["data"]["num_checkin_days"]
        print "checked:",payload["data"]["checked"]
    
        payload["data"]["checked"] = true
        data = json.dumps(payload)
        request = urllib2.Request(url,data,{'Content-Type':'application/json'})
        response = self.opener.open(request)
        result = eval(response.read())
        if result["data"].has_key("checkin_days"):
            print "第",result["data"]["checkin_days"],"天打卡"
        else:
            print "已经打过卡了"

    def today_checkin(self):
        self.open_home()
        self.login()
        self.word_study()
        #self.reading_study()
        self.checkin()
        
if __name__ == "__main__":
    sb = Shaybay("info.mine.cfg")
    sb.today_checkin()

