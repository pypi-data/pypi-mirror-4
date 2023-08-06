#-*- coding: utf-8 -*-
import twitter


import os
import sys

# parse_qsl moved to urlparse module in v2.6
try:
  from urlparse import parse_qsl
except:
  from cgi import parse_qsl

import oauth2 as oauth

REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'
AUTHORIZATION_URL = 'https://api.twitter.com/oauth/authorize'
SIGNIN_URL = 'https://api.twitter.com/oauth/authenticate'

consumer_key = '2Gp9f00Q3hmIdyjLUkOeA'
consumer_secret = 'maIkldvkkmJugi5MHWt3Fj81HNHlWmoZUsBeAeU'

if False:
    signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()
    oauth_consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)
    oauth_client = oauth.Client(oauth_consumer)
    
    print 'Requesting temp token from Twitter'
    
    resp, content = oauth_client.request(REQUEST_TOKEN_URL, 'GET')
    
    if resp['status'] != '200':
        print 'Invalid respond from Twitter requesting temp token: %s' % resp['status']
    else:
        request_token = dict(parse_qsl(content))
    
        print ''
        print 'Please visit this Twitter page and retrieve the pincode to be used'
        print 'in the next step to obtaining an Authentication Token:'
        print ''
        print '%s?oauth_token=%s' % (AUTHORIZATION_URL, request_token['oauth_token'])
        print ''
    
        pincode = raw_input('Pincode? ')
    
        token = oauth.Token(request_token['oauth_token'], request_token['oauth_token_secret'])
        token.set_verifier(pincode)
    
        print ''
        print 'Generating and signing request for an access token'
        print ''
    
        oauth_client = oauth.Client(oauth_consumer, token)
        resp, content = oauth_client.request(ACCESS_TOKEN_URL,
                                             method='POST',
                                             body='oauth_callback=oob&oauth_verifier=%s' % pincode)
        access_token = dict(parse_qsl(content))
    
        if resp['status'] != '200':
            print 'The request for a Token did not succeed: %s' % resp['status']
            print access_token
        else:
            print 'Your Twitter Access Token key: %s' % access_token['oauth_token']
            print ' Access Token secret: %s' % access_token['oauth_token_secret']
            print ''

#api = twitter.Api(consumer_key=consumer_key,
#                  consumer_secret=consumer_secret,
#                  access_token_key='14987775-dhhrNTxfgCoIBSWDC34ziVLZ2vkyGfZqaVnp4rjqs',
#                  access_token_secret='pSJrsQOWO9kkhWmmnRhZAlPTcW4ov3RaMMOpvw2w8')
api = twitter.Api()
#api.PostUpdate(status=u"test\x9cctest.")
statuses = api.GetUserTimeline("teramako")
for s in statuses:
    print s.text[:20]
#statuses = api.GetFriendsTimeline()
#for s in statuses:
#    print s.text[:20]

