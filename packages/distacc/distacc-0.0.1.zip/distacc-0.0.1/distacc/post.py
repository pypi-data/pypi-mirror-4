import twitter
import pickle
import os
import hashlib
import json
import base64

import distacc.credentials as credentials

TWEET_MAX_LENGTH = 140
SALT_LENGTH = 8

def dumps_post(password, **data):
    data = json.dumps(data, encoding = 'ascii')
    salt = os.urandom(SALT_LENGTH)
    salt = base64.b64encode(salt)
##    print 'salt:', repr(salt)
##    print 'data:', repr(data)
    to_hash = data + salt + password
    hash = base64.b64encode(hashlib.sha1(to_hash).digest())
##    print 'hash:', hash
    string = json.dumps(dict(salt = salt, hash = hash, data = data), \
                        encoding = 'ascii')
    return string

class NoResult(object):
    def __init__(self, number, reason):
        self.number = number
        self.reason = reason
        
    def __nonzero__(self):
        return False
    __bool__ = __nonzero__
    
def loads_post(password, string):
    try:
        d = json.loads(string, encoding = 'ascii')
    except ():
        return NoResult(0, 'malformed json')
    salt = d.get('salt', None)
    hash = d.get('hash', None)
    data = d.get('data', None)
    if data is None or hash is None or salt is None:
        return NoResult(1, 'information missing: data, hash or salt')
    to_hash = data + salt + password
    hash2 = base64.b64encode(hashlib.sha1(to_hash).digest())
    if hash2 != hash:
        return NoResult(2, 'wrong password')
    try:
        return json.loads(data, encoding = 'ascii')
    except ():
        return NoResult(3, 'malformed json')

data = dict(ip = '127.0.0.1', port = 1832)
s = dumps_post('password', **data)
##print s
##print len(s)
data2 = loads_post('password', s)
##print data2
##print data
assert data2 == data

HASHTAG = '#DISTAPP'

def get(password, results_per_page = 15, api = None):
    if api is None:
        api = credentials.get_api()
    page = 1
    while 1:
        posts = a.GetSearch(HASHTAG, include_entities = True, page = page)
        if not posts:
            break
        for post in posts:
            text = post.GetText()
            print 'text:', repr(text)
            if not text.startswith(HASHTAG + ' '):
                continue
            text = text[len(HASTAG) + 1:]
            result = loads_post(password)
            if result:
                return result
        page += 1

def post(password, api = None, **data):
    if api is None:
        api = credentials.get_authenticated_api()
    string = HASHTAG + ' ' + dumps_post(password, **data)
    return api.PostUpdate(string)


