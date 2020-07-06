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

old_tweets = []

consumer_key = setting.consumer_key
consumer_secret = setting.consumer_secret
access_key = setting.access_key
access_secret = setting.access_secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)

url = setting.url
def search(searchwords, set_count, bottweets):
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
        if text in bottweets:
            continue
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
                })
        headers = {
           'Content-Type': 'application/json'
        }
        urllib.request.Request(url, data=senddate.encode(), method='POST', headers=headers)

def control_arraylength():
    if len(old_tweets) > 11:
        del old_tweets[10]
        return old_tweets

def main():
    bottweets = [
            "あなたのPCに隠し味を。Serenelinuxダウンロードはこちらです。https://t.co/PfCCI4U8DG",
            "[定期]\nArch LinuxとAlter Linuxはよいぞ\nFascode Networkが開発しているAlter Linuxはこちらから\n\nhttps://t.co/n2z37xA5MQ",
            "Linux開発者の皆さん情報を共有しませんか？\nLinux使用者の皆さん開発者へ質問しませんか？\nNNLinuxやSereneLinux、caramelOS…etc\n各種チャンネルで語り合いましょう\nhttps://t.co/FRZCL7kE9N",
            "かなりの自信作でSereneLinuxにも採用されることになったので誰でも良いのでStarつけてクレメンス（自信なくてモチベ下がってる）\nhttps://t.co/qSyfHNyX7X",
            "sereneは神os\nここからダウンロード\nhttps://t.co/6Hz9349PuJ",
            "数あるLinuxディストリビューションの中でも軽量、そして使いやすいAlter LinuxとSerene Linuxをこの機会にぜひ使ってみませんか？ \n ダウンロードはここから！ \n https://t.co/ojYqqauBR6",
            "【定期】\nSereneLinuxというUbuntuベースのOSを開発中\nhttps://t.co/MF0vwo7WAO"
            ]
    while True:
        detected_tweets = search("(Serene Linux) OR SereneLinux OR  (Alter Linux) OR AlterLinux OR Fascode OR (Fascode Network) OR FascodeNetwork OR AlterISO OR F@scode OR Fasc0de OR F@sc0de exclude:retweets", 10, bottweets)
        if detected_tweets == []:
            print("Could not be found ")
        else:
            post_tweets(detected_tweets)
            control_arraylength()
        time.sleep(15)

if __name__ == '__main__':
    main()
