# Search Tweets
## 使い方
1. .envファイルを作成

    .env.sampleをご参照ください。


2. fascode_search_tweets.pyを実行

    15秒間隔でツイートされます。search関数の第二引数を任意の値に設定し、適当な検索間隔を設定してください。
    ログ出力のためrootで実行してください。

Systemd Unitファイルも添付しております。 /usr/local/share/search_tweets/fascode_search_tweets.pyを実行する前提で記述されております。

## 依存関係
tweepy, python-dotenvが必要です。pipで導入してください。
※補足 url_secretは他チャンネルに送信するための機能です。不要な方は適度コメントアウトをお願いします。
<h2>〈FascodeNetworkと開発者について〉</h2>
<a href="https://fascode.net/">Fascode Network</a>は学生を主体とする創作チームです。<br>
<a href="https://fascode.net/projects/linux/alter/">AlterLinux</a>と<a href="https://fascode.net/projects/linux/serene/">SereneLinux</a>の開発を行っています。

<h3>公式Twitterアカウント</h3>
<a href="https://twitter.com/FascodeNetwork">
        <img src="https://pbs.twimg.com/profile_images/1245716817831530497/JEkKX1XN_400x400.jpg" width="100px">
</a>
<a href="https://twitter.com/Fascode_JP">
        <img src="https://pbs.twimg.com/profile_images/1245682659231068160/Nn5tPUvB_400x400.jpg" width="100px">
</a>

<h3>開発者Twitterアカウント</h3>
<a href="https://twitter.com/YangDevJP">
        <img src="https://avatars0.githubusercontent.com/u/47053316" width="100px">
</a>

