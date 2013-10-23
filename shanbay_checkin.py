#!/usr/bin/env python2.7
#encoding=utf-8

import urllib
import urllib2
import cookielib
import json

null = "null"
true = "true"
false = "false"

class Shaybay:
    HOME_URL = 'http://www.shanbay.com'

    def __init__(self):
        self.cookiejar = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar),urllib2.HTTPHandler)
        self.opener.addheaders = [('User-agent','Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)')]
        self.opener.addheaders = [('content-type','application/json')]
        #urllib2.install_opener(opener)
        
    def print_cookies():
        for cookie in cookiejar:
            print cookie.name
            print cookie.value
    
    def open_home():
        request = urllib2.Request(HOME_URL)
        return opener.open(request).read()
    
    def login(username,password):
        loginurl = 'http://www.shanbay.com/accounts/login/'
        token = ""
        for c in cookiejar:
            if c.name=='csrftoken':
                token = c.value 
    
        params = {
            "username":username,
            "password":password,
            "login":"",
            "csrfmiddlewaretoken":token
        }
        url_data = urllib.urlencode(params)
        request = urllib2.Request(loginurl)
        response = opener.open(request,url_data)
        print "登录成功"
    
    def punch():
        url = 'http://www.shanbay.com/api/v1/checkin/?for_web=true'
        headers = {
        "Content-Type":"application/json"
        }
    
        request = urllib2.Request(url)
        response = opener.open(request)
        payload = eval(response.read())
        print "num_checkin_days:",payload["data"]["num_checkin_days"]
        print "checked:",payload["data"]["checked"]
    
        payload["data"]["checked"] = true
        data = json.dumps(payload)
        request = urllib2.Request(url,data,{'Content-Type':'application/json'})
        response = opener.open(request)
        result = eval(response.read())
        if result["data"].has_key("checkin_days"):
            print "第",result["data"]["checkin_days"],"天打卡"
        else:
            print "已经打过卡了"

if __name__ == "__main__":
    open_home()
    login(USERNAME,PASSWORD)
    punch()
