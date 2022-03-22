import mysql.connector




def storeToMySqlDB(dataToStore, tableToStore):

  mydb = mysql.connector.connect(
    host="localhost",
    user="user_01",
    password="SecretPassw0rd1",
    database="tweets_with_counts"
  )

  mycursor = mydb.cursor()

  #print("INSERTing  " + str(len(dataToStore)) + " in mysql table: " + str(tableToStore))
  for entry in dataToStore:
    sql = """ INSERT INTO """ + str(tableToStore) + """ (id, retweetCount, favouriteCount) 
    VALUES(%s, %s, %s) ON DUPLICATE KEY UPDATE    
    retweetCount=%s, favouriteCount=%s"""
    val = (entry.id, entry.retweetCount, entry.favouriteCount, entry.retweetCount, entry.favouriteCount)
    #sql = "INSERT INTO customers (name, address) VALUES (%s, %s)"
    #val = ("John", "Highway 21")
    mycursor.execute(sql, val)

    

  mydb.commit()
  #print(mycursor.rowcount, "record(-s) stored in "+ str(tableToStore) +".")
  mycursor.close() 

