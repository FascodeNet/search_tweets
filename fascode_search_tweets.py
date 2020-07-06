#!/usr/bin/env python3
# Yang Niao
# Twitter: @YangDevJP
# Email  : yang@fascode.net
#
# (c) 2019-2020 Fascode Network.
#
# search_tweets.py
#
# The main script that runs the search tweets about fascode.
#


import tweepy
import json
import time
import setting
import urllib
import json
import time
import datetime

old_tweets = []

consumer_key = setting.consumer_key
consumer_secret = setting.consumer_secret
access_key = setting.access_key
access_secret = setting.access_secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)

url = setting.url
def search(searchwords, set_count):
    # 現在の時刻
    results = api.search(q=searchwords, count=set_count)
    detected_tweets = []
    for result in results:
        status_n = result._json['id']
        if status_n in old_tweets:
            return detected_tweets
        else:
            old_tweets.append(status_n)

        text = result._json['text']
        username = result.user._json['screen_name']
        url = "https://twitter.com/" + username + "/status/" + str(status_n)
        icon = result.user._json['profile_image_url_https']
        detected_tweets.append([status_n, username, url, icon, text])
        print("Found new tweet!")
        print("USER: " + username + "\nTEXT: " + text + "\n\nLink: " + url + "\nICON: " + icon)
    return detected_tweets

def post_tweets(detected_tweets):
    for tweet in detected_tweets:
        senddate = json.dumps({ 
                "icon_url":tweet[3],
                "username":str(tweet[1]),
                "text": tweet[4] + '\n' + tweet[2]
                }, ensure_ascii=False)
        headers = {
           'Content-Type': 'application/json'
        }
        response = urllib.request.Request(url, data=senddate.encode(), method='POST', headers=headers)
        try:
            with urllib.request.urlopen(response) as response:
                status = str(response.getcode())
                with open('/var/log/search_tweets.log', mode='a')  as f:
                    dt_now = datetime.datetime.now()
                    time = dt_now.strftime('%Y/%m/%d %H:%M:%S.%f')
                    writeline = ['HTTP return code: ', status, '\n', 'tiemcode: ', time, '\n', senddate.replace(',', '\n').replace('\\n', '\n "link": \"').replace('{', ' ').replace('}', ''), '\n']
                    f.writelines(writeline)
                    

        except urllib.error.URLError as e:
            with open('/var/log/search_tweets.err', mode='a')  as f:
                print(e.reason)

def control_arraylength():
    if len(old_tweets) > 11:
        del old_tweets[10]
        return old_tweets

def main():
    while True:
        detected_tweets = search("(Serene Linux) OR SereneLinux OR  (Alter Linux) OR AlterLinux OR Fascode OR (Fascode Network) OR FascodeNetwork OR AlterISO OR F@scode OR Fasc0de OR F@sc0de exclude:retweets -source:twittbot.net", 10)
        if detected_tweets == []:
            print("Could not be found ")
        else:
            post_tweets(detected_tweets)
            control_arraylength()
        time.sleep(15)

if __name__ == '__main__':
    main()
