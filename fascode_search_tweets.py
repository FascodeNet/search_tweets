#!/usr/bin/env python3
# Yang Niao
# Twitter: @yangniao23
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


#引数: 検索ワード, 検索する件数, apiのインスタンス  機能: 検索結果を2次元リストで返す  リスト形式: [[ツイートID, ユーザ名, ツイートID, アイコン, ツイート本文], [ツイートID, …]]
def search(searchwords, set_count, api, old_tweets):
    try:
        results = api.search(q=searchwords, count=set_count, tweet_mode="extended")
    except tweepy.TweepError as e:
        with open('/var/log/search_tweets.err', mode='a')  as f:
            f.write('\n' + "get error: " + e)
            f.write('\n' + "reason: " + e.reason + '\n')
        if e.reason == "[{'message': 'Rate limit exceeded', 'code': 88}]":
                # 15分待つのに，いつ処理が止まったか時間を表示。
                print(datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
                time.sleep(60 * 15)
        return search(searchwords, set_count, api, old_tweets)
            
    detected_tweets = []
    for result in results:
        status_n = result._json['id']
        if status_n in old_tweets:
            old_tweets.extend([result._json['id'] for result in results])
            control_arraylength(old_tweets)
            return (detected_tweets, old_tweets)

        text = result._json['full_text']
        username = result.user._json['screen_name']
        url = "https://twitter.com/" + username + "/status/" + str(status_n)
        icon = result.user._json['profile_image_url_https']
        detected_tweets.append([status_n, username, url, icon, text])

    old_tweets.extend([result._json['id'] for result in results])
    control_arraylength(old_tweets)
    return (detected_tweets, old_tweets)


"""
tweet[0] == ツイートID
tweet[1] == ユーザ名
tweet[2] == ツイートのURL
tweet[3] == ユーザのアイコン
tweet[4] == ツイート本文
"""

# 検出されたツイートを公開チャンネルのWebhookに投げる形式に整形し, webhookに投げる関数を呼び出す
def post_tweets(url, tweet):
    senddate = json.dumps({
            "icon_url":tweet[3],
            "username":str(tweet[1]),
            "text": tweet[4] + '\n' + tweet[2]
            }, ensure_ascii=False)
    post_tweet_to_webhook(url, senddate)

# 検出されたツイートを鍵チャンネルのWebhookに投げる形式に整形し, webhookに投げる関数を呼び出す
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
                        "name": "🗩返信",
                        "integration": {
                            "url": "https://fascode.net/api/mattermost/replytw.php?twurl=" + tweet[2],
                            "context": {
                                "action": "do_something_ephemeral"
                            },
                        },
                    }, {
                        "name": "🗘リツイート",
                        "integration": {
                            "url": "https://fascode.net/api/mattermost/rttw.php?twurl=" + tweet[2],
                            "context": {
                                "action": "do_something_ephemeral"
                            },
                        },
                    }, {
                        "name": "♥いいね",
                        "integration": {
                            "url": "https://fascode.net/api/twitter/iine.php?id=" + str(tweet[0]),
                            "context": {
                                "action": "do_somethings_ephemeral"
                            },
                        },
                    },
                    ]
                },
                ]
            }, ensure_ascii=False)
    post_tweet_to_webhook(url_secret, senddate)

def post_dm_secret(url_secret, dm):
    pass

# 整形されたデータをWebhookに投げる  同時にログの書き込みも行う
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
            f.write('\n' + "post error: " + e.reason)

# 最終取得ツイートIDを記録し, 重複取得を回避する
def write_lasttweets(old_tweets):
    with open('/var/log/search_tweets.lasttweets', mode='w') as f:
        f.write(",".join(map(str, old_tweets)))

# リスト長を調節する
def control_arraylength(old_tweets):
    if len(old_tweets) >=  10:
        # 末尾10項目を列挙しそれで上書きする
        old_tweets = [old_tweets[len(old_tweets) - 10 + i] for i in range(10)]
        write_lasttweets(old_tweets)
    else:
        write_lasttweets(old_tweets)

    return old_tweets

# 新規DMを受け取りWebhookに投げる
def getdmposttowebhook(api, lastid):
    pass

def readlog(path):
    if os.path.exists(path):
        if os.stat(path).st_size == 0:
            with open('/var/log/search_tweets.err', mode='a')  as f:
                f.write('warning: ' + path + "is empty.\n")
                return [0]
        else:
            with open(path, mode='r') as f:                
                return [int(x.strip()) for x in f.read().split(',')]
    else:
        with open('/var/log/search_tweets.err', mode='a')  as f:
                f.write('warning: ' + path + "is not found.\n")
                return [0]

# 総合処理
def main():
    old_tweets = readlog(r'/var/log/search_tweets.lasttweets')
    old_tweets = control_arraylength(old_tweets)

    consumer_key = setting.consumer_key
    consumer_secret = setting.consumer_secret
    access_key = setting.access_key
    access_secret = setting.access_secret
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)

    url = setting.url
    url_secret = setting.url_secret

    count = 0
    while True:
        
        detected_tweets, old_tweets = search('(("Serene" "Linux") OR "SereneLinux" OR  ("Alter" "Linux") OR "AlterLinux" OR "Fascode" OR ("Fascode" "Network") OR "FascodeNetwork" OR "AlterISO") OR ("LUBS" lang:ja) OR ("水瀬玲音"  -"水瀬玲音 おみくじ を引きました") OR ("せれねあーと" OR "#せれねあーと") -("おみくじ" OR "天気予報") exclude:retweets -source:twittbot.net', 10, api, old_tweets)
        if not detected_tweets == []:
            for tweet in detected_tweets:
                post_tweets(url, tweet)
                post_tweets_secret(url_secret, tweet)
        time.sleep(15)
        count += 1

def test():
    old_tweets = readlog(r'/var/log/search_tweets.lasttweets')
    old_tweets = control_arraylength(old_tweets)

    consumer_key = setting.consumer_key
    consumer_secret = setting.consumer_secret
    access_key = setting.access_key
    access_secret = setting.access_secret
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)


    count = 0
    while True:
        
        detected_tweets, old_tweets = search('(("Serene" "Linux") OR "SereneLinux" OR  ("Alter" "Linux") OR "AlterLinux" OR "Fascode" OR ("Fascode" "Network") OR "FascodeNetwork" OR "AlterISO") OR ("LUBS" lang:ja) OR ("水瀬玲音"  -"水瀬玲音 おみくじ を引きました") OR ("せれねあーと" OR "#せれねあーと") -("おみくじ" OR "天気予報") exclude:retweets -source:twittbot.net', 10, api, old_tweets)
        if not detected_tweets == []:
            for tweet in detected_tweets:
                print("Username: " + tweet[1])
                print("ID      : " + str(tweet[0]))
                print("Text    :\n" + tweet[4])
        print(count)
        time.sleep(15)
        count += 1
if __name__ == '__main__':
    main()
    #test()