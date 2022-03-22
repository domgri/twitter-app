
import mysql.connector
import datetime

mydb = mysql.connector.connect(
    host="localhost",
    user="user_01",
    password="SecretPassw0rd1",
    database="tweets_with_counts"
  )

def getTweets(table, batchesNum, batchSize):
    global mydb
    mycursor = mydb.cursor()
    mycursor.execute("SELECT id, retweetCount, favouriteCount FROM {table} LIMIT {number}".format(table = table, number = batchesNum * batchSize))
    myresult = mycursor.fetchall()
    return myresult

def getTrendingTweetsFromNew(table, batchesNum, batchSize, threshold):
  global mydb
  mycursor = mydb.cursor()
  mycursor.execute("""SELECT id, retweetCount, favouriteCount FROM {table} WHERE retweetCount >= {threshold} OR favouriteCount >= {threshold} 
    LIMIT {number}""".format(table = table, number = batchesNum * batchSize, threshold = threshold))
  myresult = mycursor.fetchall()
  return myresult

def deleteTweets(table, batchesNum, batchSize):
    global mydb

    mycursor = mydb.cursor()
    sql = "DELETE FROM {table} LIMIT {number}".format(table = table, number = batchesNum * batchSize)
    mycursor.execute(sql)
    mydb.commit()
    print(mycursor.rowcount, "record(-s) deleted from from "+ str(table) +" (did not meet trending threshold).")
    mycursor.close() 

def storeTweets(table, tweetsData, threshold):
  global mydb
  mycursor = mydb.cursor()

  count = 0

  for entry in tweetsData:
    if entry.retweetCount >= threshold or entry.favouriteCount >= threshold:
      sql = """INSERT INTO {table} (id, retweetCount, favouriteCount, timeStamp) VALUES({id}, {retweets}, {favourites}, \"{timeStamp}\") ON DUPLICATE KEY UPDATE 
      retweetCount={retweets}, favouriteCount={favourites};""".format(table = table, id = entry.id, retweets = entry.retweetCount, favourites = entry.favouriteCount, timeStamp = datetime.datetime.now())
      mycursor.execute(sql)
      count += 1

      

  mydb.commit()
  print(count, "record(-s) stored in "+ str(table) +".")
  mycursor.close() 


def storeNewestTweets(table, tweets):
  global mydb
  mycursor = mydb.cursor()

  for entry in tweets:
      print(entry.id)
      sql = """INSERT INTO {table} (id, retweetCount, favouriteCount, timeStamp) VALUES({id}, {retweets}, {favourites}, \"{timeStamp}\") ON DUPLICATE KEY UPDATE 
      retweetCount={retweets}, favouriteCount={favourites};""".format(table = table, id = entry.id, retweets = entry.retweetCount, favourites = entry.favouriteCount, timeStamp = datetime.datetime.now())
      mycursor.execute(sql)

      

  mydb.commit()
  print(mycursor.rowcount, "record(-s) stored in "+ str(table) +".")
  mycursor.close() 


def reorderTrending(table, batchesNum, batchSize, threshold):

  global mydb
  mycursor = mydb.cursor()
  sql = "SELECT COUNT(*) FROM {table};".format(table = table)
  mycursor.execute(sql)
  myresult = mycursor.fetchall()

  if len(myresult) > (batchesNum * batchSize):
    tweets = getTweets(table, batchesNum, batchSize)
    deleteTweets(table, batchesNum, batchSize)
    storeTweets(table, tweets, threshold)




