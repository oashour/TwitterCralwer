import urllib
from bs4 import BeautifulSoup 

url = "http://wikipedia.org"

urls= [url] # stack of urls to scrape
visited = [url] # historic record of urls

htmltext = "failure"

while len(urls) > 0:
    try:
        htmltext = urllib.urlopen(urls[0]).read()
    except:
        print("fail: ", urls[0])
    
    soup = BeautifulSoup(htmltext)
    
    urls.pop(0)
    
    print(soup.findAll('a', href=True))

