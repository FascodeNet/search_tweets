#!/usr/bin/env python3
# Yang Niao
# Twitter: @YangDevJP
# Email  : yang@fascode.net
#
# (c) 2019-2020 Fascode Network.
#
# initial_and_end_process.py
#
# Functions in the script that runs when before run fascode_search_tweets.py or end it.
#

import os
import sys
import fascode_search_tweets

def initial_process():
    if not os.path.exists('/var/log/search_tweets.lasttweets'):
        return []

    with open('/var/log/search_tweets.lasttweets', mode='r') as f:
        return [int(x.strip()) for x in f.read().split(',')]

def end_process(old_tweets):
    with open('/var/log/search_tweets.lasttweets', mode='w') as f:
        f.write(",".join(map(str, old_tweets)))

def _help():
    body = """
    Usage:
        initial_and_end_process.py [-i|-e]

    Option:
        -i:  read /var/log/search_tweets.lasttweets and hand over to fascode_search_tweets.main()  (Can be omitted.)
        -e:  write /var/log/search_tweets.lasttweets that fascode_search_tweets.old_tweets
    """
    print(body)

def main():
    if len(sys.argv) == 1:
        fascode_search_tweets.main(initial_process())
    if len(sys.argv) == 2:
        if sys.argv[1] == '-i':
            fascode_search_tweets.main(initial_process())
        elif sys.argv[1] == '-e':
            end_process(fascode_search_tweets.old_tweets)
            fascode_search_tweets.end_process()
            exit(0)
        else:
            print("Invalid args.")
            _help()
            exit(1)
        
if __name__ == '__main__':
    main()