# Import modules
from TwitterAPI import TwitterAPI
from TwitterAPI import TwitterRestPager
from tabulate import tabulate
import urllib.request
import os
import time

# Connect to the API
apiKey="lNPmHMmEPYajuMltc2KuJuzMv"
apiSecret="B21Nh5x4yFbjesT47nsR1wJX4puMwmuNWQAMARw0sAWYeIEqc6"
accessToken="59862114-THjs0rdX6YSKgcKMqy3EVaocauLTkVODrhB2TNI9u"
accessTokenSecret="tB9RUnEO8dGPCjKWTOqpQPpnvtB1VRay9fRUYqEPIM3qX"
api = TwitterAPI(apiKey, apiSecret, accessToken, accessTokenSecret)

# Script Parameters:
query = "Egypt" # what to search for
lang = "-"     # what language to restrict to
nTweets = 100   # how many total tweets
nFlush = 100    # flush stream every 100 tweets
media = False     # find tweets with media or not. use "-" for don't care. 
mSize = 'medium' #quality of picture 
dlMedia = True 
cacheMedia = False 


# Create directories and files, etc.
time = time.strftime("%d_%b_%Y_%H.%M.%S") 
if dlMedia:
    workDir = time

if cacheMedia & dlMedia:
    workDir = "cache"

if not os.path.exists(workDir):
    os.makedirs(workDir)
os.chdir(workDir)
f = open(time+".txt", "w")

# Create counters
current = 0
total = 0
data = []
stream = []
# Create table header for printing
tableHeader=["Handle", "Name", "Text", "Time stamp", 
             "Hashtags", "Retweets", "Favorites", "Media", "Language"]
# tableHeader=["Handle", "Name", "Text", "Time stamp", "Retweets", "Favorites"]

# Search
r = TwitterRestPager(api, 'search/tweets', {'q':query, 'count':100})

# For each tweet
for tweet in r.get_iterator(wait=6):
    if 'text' in tweet: # if it's really a tweet and not something else

        # Check if it fits the media requirements (yes, no, don't care)
        if media != "-":
            cMedia = True if media == True else False 
            if ('media' not in tweet['entities']) & (cMedia == True):
                continue 
            elif ('media' in tweet['entities']) & (cMedia == False):
                continue
        else:
            if 'media' in tweet['entities']:
                cMedia = True 
            else:
                cMedia = False 

        # Check if it fits the language requirements (anything or specific)
        if lang != "-":
            tLang = lang
            if tweet['metadata']['iso_language_code'] != tLang:
                continue
        else:
            tLang = tweet['metadata']['iso_language_code']

        # If no hashtags
        if tweet['entities']['hashtags']:
            hashtags = "" 
            for tag in tweet['entities']['hashtags']:
                hashtags + tag['text'] + ", "
        else:
            hashtags = "-"

        # Push the tweet onto the stream stack
        stream.append([tweet['user']['name'], tweet['user']['screen_name'], 
                    tweet['text'].replace('\n', ' '), tweet['created_at'],
                    hashtags, tweet['retweet_count'], tweet['favorite_count'],
                    cMedia, tLang]) 

        if cMedia & dlMedia:
            cMedia += len(tweet['entities']['media'])
            mediaURL = tweet['entities']['media'][0]['media_url']
            fileName = str(total)+mediaURL[-4:] # last 4 are extension 
            urllib.request.urlretrieve(mediaURL+":"+mSize, fileName)

        # increment the counters
        current += 1
        total += 1

        # every 100 tweets, flush the stream to improve performance and add to a big stream
        if current == nFlush:
            data.extend(stream) # concatenate
            stream = []         # empty stack
            current = 0         # reset counter
        
        # max number of tweets
        if total >= nTweets:
            data.extend(stream) # concatenate
            break
    # this should not trigger, but just in case
    # this handles an exception triggered when we send more than 1 request every 5 seconds
    # this would result in a 15 minute block
    elif 'message' in item and item['code'] == 88:
        print('SUSPEND, RATE LIMIT EXCEEDED: %s' % item['message'])
        break
    #print(count)

# print table
f.write(tabulate(data, headers=tableHeader, tablefmt='fancy_grid'))
