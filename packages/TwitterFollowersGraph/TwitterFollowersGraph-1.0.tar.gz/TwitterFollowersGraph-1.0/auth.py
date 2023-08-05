import tweepy

# OAUTH AUTENTICATION                                                           
# Comunidades App keys                                                                
CONSUMER_KEY = '7it3IkPFI4RNIGhIci5w'
CONSUMER_SECRET = 'zGUE2bTucHcNn5IxFNyBP8dN2EvbrMtij5xuWHqcW0'

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)

def get_api():
    """ Authorize API to use user's account """

    try:
        redirect_url = auth.get_authorization_url()
    except tweepy.TweepError:
        print 'Error! Failed to get request token.'

    print ("Please go to the next URL and get your authorization number:\n %s" % redirect_url)
    verifier = raw_input('Authorization Number:')

    token = auth.get_access_token(verifier) #token includes ACCES KEY and SECRET                                                                                               
    api = tweepy.API(auth)
    return api

