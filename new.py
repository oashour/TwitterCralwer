import requests
from bs4 import BeautifulSoup

url = "https://twitter.com/search?q=NadineJonah&src=typd"
#url = "http://omarashour.com"
r = requests.get(url, prefetch=False)

soup = BeautifulSoup(r.content, "lxml")

links = soup.findAll("a")

#for link in links:
    #if "http" in link.get("href"):
#        print "<a href='%s'>%s</a>" %(link.get("href"), link.text) 
        
g_data = soup.findAll("p", {"class": "js-tweet-text tweet-text"})

for item in g_data:
    print(item.text)
    print("------------------------------------------------------")
