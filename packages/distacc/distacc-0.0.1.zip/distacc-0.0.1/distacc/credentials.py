import os
import pickle
import twitter

## get credentials like these:
## consumer_key='twitter consumer key',
## consumer_secret='twitter consumer secret',
## access_token_key='the_key_given',
## access_token_secret='the_key_secret'

credentials = pickle.load(open(os.path.join(os.path.dirname(__file__), 'twitter_credentials.pickle')))

def get_api():
    return twitter.Api()

def get_authenticated_api():
    return twitter.Api(**credentials)
