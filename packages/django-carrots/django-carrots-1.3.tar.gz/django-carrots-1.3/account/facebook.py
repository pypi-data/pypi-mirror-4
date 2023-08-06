from urllib import urlencode, urlopen
from httplib2 import Http


def dsa_urlopen(*args, **kwargs):
    return urlopen(*args, **kwargs)

def facebook_request(url, access_token, params=None, data=None):
    h = Http()
    params = {} if params is None else params.copy()
    params['access_token'] = access_token
    url = url + '?' + urlencode(params)
    if data is None:
        resp, content = h.request(url, "GET")
    else:
        resp, content = h.request(url, "POST", urlencode(data))
    return content

FACEBOOK_API_URL = 'https://graph.facebook.com/'
FACEBOOK_FEED = 'me/feed'

def publish_to_facebook(user, contents):

    try:
        social_auth = user.social_auth.filter(provider="facebook")[0]
    except IndexError:
        raise Exception("No social auth profile available for this user.")

    token = social_auth.tokens['access_token']
    url = FACEBOOK_API_URL+FACEBOOK_FEED
    data = {
        "message": unicode(contents).encode('utf-8'),
    }
    result = facebook_request(url, token, data=data)
    print result

