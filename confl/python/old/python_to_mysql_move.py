import mysql.connector



mydb = mysql.connector.connect(
    host="localhost",
    user="user_01",
    password="SecretPassw0rd1",
    database="tweets_with_counts"
  )


def getTrendingStringArray(tableToSelectFrom, NUMBER_API_CAN_HANDLE):
  mycursor = mydb.cursor()
  sql = "SELECT id FROM " + str(tableToSelectFrom) + ";"
  mycursor.execute(sql)
  ids = mycursor.fetchall()

  stringBatchesForCalls = []

  while len(ids) > 0:
    #print(ids)
    if len(ids) > NUMBER_API_CAN_HANDLE:
      idsStr = ','.join(str(e[0]) for e in ids[:NUMBER_API_CAN_HANDLE])
      stringBatchesForCalls.append(idsStr)
      ids = ids[NUMBER_API_CAN_HANDLE:]
    else:
      idsStr = ','.join(str(e[0]) for e in ids)
      stringBatchesForCalls.append(idsStr)
      ids = []
      #print(ids)
  

  return stringBatchesForCalls

  # print(len(ids))
  # idsStr = ','.join(str(e[0]) for e in ids)
  # print(idsStr)




def deleteNotPopular():
  mycursor = mydb.cursor()

  sql = "DELETE FROM tweet_counts"
  mycursor.execute(sql)
  mydb.commit()
  print(mycursor.rowcount, "record(-s) deleted from from tweet_counts (not popular).")
  mycursor.close() 



def checkIfSomethingToMove(threshold):
 
  mycursor = mydb.cursor()

  # sql = """ START TRANSACTION; 
  #     INSERT INTO trending_tweet_counts (id, retweetCount, favouriteCount) 
  #     SELECT id, retweetCount, favouriteCount 
  #     FROM tweet_counts 
  #     WHERE retweetCount >= %s OR favouriteCount >= %s; 

  #     DELETE FROM tweet_counts 
  #     WHERE retweetCount >= %s OR favouriteCount >= %s; 

  #     COMMIT;"""

  # New policy: deletes later all that were not taken

  sql = """
    INSERT IGNORE INTO trending_tweet_counts (id, retweetCount, favouriteCount) 
    SELECT id, retweetCount, favouriteCount 
    FROM tweet_counts 
    WHERE retweetCount >= %s OR favouriteCount >= %s; """



  val = (threshold, threshold)
  mycursor.execute(sql, val)
  #mycursor.fetchall()


  mydb.commit()
  print(mycursor.rowcount, "record(-s) moved from tweet_counts to trending_tweet_counts.")

  mycursor.close() 

