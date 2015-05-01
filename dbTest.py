import sqlite3

def updateDB(tweets):
    db = sqlite3.connect('db.sqlite3')
    cursor = db.cursor()
#    cursor.execute('''DROP TABLE tweets''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS 
        tweets(id INTEGER PRIMARY KEY, name TEXT, handle TEXT, content TEXT, time TEXT,
               hashtags TEXT, rtCount INTEGER, favCount INTEGER, media INTEGER, lang TEXT, 
               imgName TEXT)
    ''')
    db.commit()
    
    cursor.executemany('''
        INSERT INTO tweets(name, handle, content, time, hashtags, rtCount, favCount, 
                          media, lang, imgName)
        VALUES(:name, :handle, :content, :time, :hashtags, :rtCount, :favCount, :media,
               :lang, :imgName)''', tweets)
    print('Tweets inserted')
     
    db.commit()
    #cursor.execute('''SELECT * FROM tweets''')
    #for row in cursor:
        # row[0] returns the first column in the query (name), row[1] returns email column.
    #    print(row)

def main():
    tweet1 = {'name': "Sharmoot", 'handle': "Sharmat101", 'content': "Ana sharmoot neik",
              'time': "April 30 69:69 AM", 'hashtags': "sharmoot, neik", 'rtCount': 69,
              'favCount': 6969, 'media': False, 'lang': 'sr', 'imgName': "sharmoot.jpg"}

    tweet2 = {'name': "Metnak", 'handle': "Manyook101", 'content': "Ana metnak neik",
              'time': "August 29 69:69 AM", 'hashtags': "metnak, neik", 'rtCount': 123,
              'favCount': 456, 'media': 3, 'lang': 'mn', 'imgName': "metnak.jpg"}
    tweets = [tweet1, tweet2]

    updateDB(tweets)

if __name__=="__main__":
    main()
