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
import datetime
import os

old_tweets = []

def search(searchwords, set_count, api):
    results = api.search(q=searchwords, count=set_count, tweet_mode="extended")
    detected_tweets = []
    for result in results:
        status_n = result._json['id']
        if status_n in old_tweets:
            return detected_tweets
        else:
            old_tweets.append(status_n)

        text = result._json['full_text']
        username = result.user._json['screen_name']
        url = "https://twitter.com/" + username + "/status/" + str(status_n)
        icon = result.user._json['profile_image_url_https']
        detected_tweets.append([status_n, username, url, icon, text])
        print("Found new tweet!")
        print("USER: " + username + "\nTEXT: " + text + "\n\nLink: " + url + "\nICON: " + icon)
    return detected_tweets

"""
tweet[0] == ツイートID
tweet[1] == ユーザ名
tweet[2] == ツイートのURL
tweet[3] == ユーザのアイコン
tweet[4] == ツイート本文
"""

def post_tweets(url, url_secret, detected_tweets):
    for tweet in detected_tweets:
        senddate = json.dumps({
                "icon_url":tweet[3],
                "username":str(tweet[1]),
                "text": tweet[4] + '\n' + tweet[2]
                }, ensure_ascii=False)
        post_tweets_secret(url_secret, tweet)
        post_tweet_to_webhook(url, senddate)

def post_tweets_secret(url_secret, tweet):
    senddate = json.dumps({
                "icon_url":tweet[3],
                "username":str(tweet[1]),
                "attachments": [
                {
                    "pretext": tweet[2],
                    "text": tweet[4],
                    "update": {"message": tweet[4] + '\n' + tweet[2] },
                    "actions": [
                    {
                        "name": "Favorite this tweet",
                        "integration": {
                            "url": "https://fascode.net/api/twitter/iine.php?id=" + str(tweet[0]),
                            "context": {
                                "action": "do_somethings"
                            },
                        },
                    }, {
                        "name": "Reply this tweet",
                        "integration": {
                            "url": "https://fascode.net/api/mattermost/replytw.php?twurl=" + tweet[2],
                            "context": {
                                "action": "do_somethings"
                            }
                        }
                    }
                        
                    ]
                }
                ]
            }, ensure_ascii=False)
    post_tweet_to_webhook(url_secret, senddate)

def post_tweet_to_webhook(url, senddate):
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

def write_lasttweets():
    with open('/var/log/search_tweets.lasttweets', mode='w') as f:
        f.write(",".join(map(str, old_tweets)))

def control_arraylength():
    if len(old_tweets) > 11:
        del old_tweets[10]
        write_lasttweets()
        return old_tweets
    else:
        write_lasttweets()


end_process = lambda: exit(0)

def main():
    if os.path.exists('/var/log/search_tweets.lasttweets'):
        with open('/var/log/search_tweets.lasttweets', mode='r') as f:
            global old_tweets
            old_tweets = [int(x.strip()) for x in f.read().split(',')]

    consumer_key = setting.consumer_key
    consumer_secret = setting.consumer_secret
    access_key = setting.access_key
    access_secret = setting.access_secret
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)

    url = setting.url
    url_secret = setting.url_secret
    while True:
        detected_tweets = search('(("Serene" "Linux") OR "SereneLinux" OR  ("Alter" "Linux") OR "AlterLinux" OR "Fascode" OR ("Fascode" "Network") OR "FascodeNetwork" OR "AlterISO") OR ("LUBS" lang:ja) OR ("水瀬玲音"  -"水瀬玲音 おみくじ を引きました") OR ("せれねあーと" OR "#せれねあーと") -("おみくじ" OR "天気予報") exclude:retweets -source:twittbot.net', 100, api)
        if detected_tweets == []:
            print("Could not be found ")
        else:
            post_tweets(url, url_secret, detected_tweets)
            control_arraylength()
        time.sleep(10)

if __name__ == '__main__':
    main()
