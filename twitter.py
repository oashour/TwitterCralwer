# Import modules
from TwitterAPI import TwitterAPI
from TwitterAPI import TwitterRestPager
from tabulate import tabulate
import urllib.request
import os
import time

# Connect to the API
def fetch_tweets(apiKey, apiSecret, accessToken, accessTokenSecret,
                 query, lang='-', nTweets=100, nFlush=100, media='-',
                 mSize='medium', saveMedia="False", viewMedia="True",
                 workDir='cache', saveLog="True", logName='log.txt'):

    api = TwitterAPI(apiKey, apiSecret, accessToken, accessTokenSecret)

    # Create directories and files, etc.
    curTime = time.strftime("%d_%b_%Y_%H.%M.%S")
    if not saveMedia:
        workDir = "cache"

    if viewMedia:
        if not os.path.exists(workDir):
            os.makedirs(workDir)
        os.chdir(workDir)

    if saveLog:
        f = open(logName, "w")

    print("Started fetching will following parameters:")
    print("query: ", query)
    print("lang: ", lang)
    print("nTweets: ", nTweets)
    print("nFlush: ", nFlush)
    print("media: ", media)
    print("mSize: ", mSize)
    print("viewMedia: ", viewMedia)
    print("saveMedia: ", saveMedia)
    print("workDir: ", workDir)
    print("saveLog: ", saveLog)
    print("logName: ", logName)

    # Create counters
    current = 0
    total = 0
    data = []
    stream = []
 
    # Create table header for printing
    tableHeader=["Name", "Handle", "Text", "Time stamp", "Hashtags", 
                 "Retweets", "Favorites", "Media", "Language", "Img Path"]
    keys = ["name", "handle", "text", "time", "hashtags", "rtCount", 
            "favCount", "media", "lang", "imgName"]

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
                    hashtags = hashtags + tag['text'] + ", "
            else:
                hashtags = "-"

            fileName = None

            if cMedia & viewMedia:
                cMedia += len(tweet['entities']['media'])
                mediaURL = tweet['entities']['media'][0]['media_url']
                fileName = str(total)+mediaURL[-4:] # last 4 are extension 
                urllib.request.urlretrieve(mediaURL+":"+mSize, fileName)

            # Push the tweet onto the stream stack
            stream.append([tweet['user']['name'], tweet['user']['screen_name'], 
                        tweet['text'].replace('\n', ' '), tweet['created_at'],
                        hashtags, tweet['retweet_count'], tweet['favorite_count'],
                        cMedia, tLang, fileName]) 

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
    if saveLog:
        f.write(tabulate(data, headers=tableHeader, tablefmt='fancy_grid'))
    
    #for i in range(total):
    #    print(data[i]) 
    result = []
    dictList = []
    for i in range(total):
        dictList.append(dict(zip(keys, data[i])))

    result = [dictList, total, workDir]
    os.chdir("..")
    print("Done Fetching!")

    return result


def main():
    fetch_tweets("Egypt")

if __name__ == "__main__":
    main()
