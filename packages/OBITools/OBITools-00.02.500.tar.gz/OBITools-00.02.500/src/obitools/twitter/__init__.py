import tweepy

# Request token URL    https://api.twitter.com/oauth/request_token
# Authorize URL    https://api.twitter.com/oauth/authorize
# Access token URL    https://api.twitter.com/oauth/access_token

CONSUMER_KEY = 'KD0MCpfYMaIchgiiOrrFBg'
CONSUMER_SECRET = 's9voKXzzuCHb9h0cPELZM8u7IPoNQChGn9y3o0WDuc'

def register(config=None):
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth_url = auth.get_authorization_url()
    print 'Please authorize: ' + auth_url
    verifier = raw_input('PIN: ').strip()
    auth.get_access_token(verifier)
    print "ACCESS_KEY = '%s'" % auth.access_token.key
    print "ACCESS_SECRET = '%s'" % auth.access_token.secret
    if config is not None:
        twitter_conf = open(config)
    else:    
        twitter_conf = open(".obitweet.keys")
    print >>twitter_conf,auth.access_token.key
    print >>twitter_conf,auth.access_token.secret
    twitter_conf.close()
    return auth.access_token.key,auth.access_token.secret
    
def init(config=None):
    try:
        if config is not None:
            twitter_conf = open(config)
        else:    
            twitter_conf = open(".obitweet.keys")
        ACCESS_KEY,ACCESS_SECRET=[x.strip() for x in twitter_conf]
    except:
        ACCESS_KEY,ACCESS_SECRET=register(config)
        
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(auth)

    return api


