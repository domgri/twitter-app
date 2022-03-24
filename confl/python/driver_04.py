import asyncio
import json
#from textwrap import indent
import time
import threading 
from collections import deque
from confluent_kafka import Consumer
from mysql_function_2 import getTweets, getTrendingTweetsFromNew, deleteTweets, storeTweets, reorderTrending, storeNewestTweets
from twitter_api_functions import callApi
from TweetCounts import TweetCounts
import logging

# corner case if reaches trending adn then drops - keeps in place

#TODO: TEST FUNCTION BY FUNCTION AND MAKE ASYNCHRONOUS

MAX_NUMBER_OF_TWEETS_TO_CONSUME = 900
NUMBER_OF_TWEETS_API_CAN_HANDLE = 100 # 100
NEW_TWEETS_TABLE = "new_tweets"
TRENDING_TWEETS_TABLE = "trending_tweets"
BATCHES_LIMIT = 9
BATCH_SIZE = 100
TRENDING_THRESHOLD = 10
CONSUMING_WINDOW_SECONDS = 300

messages = []
newBatches = deque()

async def getNewTweets(consumer):

    CONSUMING_WINDOW_SECONDS = 300
    timeout = time.time() + CONSUMING_WINDOW_SECONDS 

    print("Starting new tweets fetch for " + str(CONSUMING_WINDOW_SECONDS) + " seconds") 
    logging.warning("Starting new tweets fetch for " + str(CONSUMING_WINDOW_SECONDS) + " seconds")  

    try:
       
        while time.time() < timeout:
             
            records = consumer.consume(timeout=CONSUMING_WINDOW_SECONDS, num_messages=MAX_NUMBER_OF_TWEETS_TO_CONSUME)

            if not records:
                #print("Nothing to consume, sleeping (for " + str(timespan/10) +" seconds)")
                #time.sleep(timespan/10)
                #print("0 records consumed")
                pass
            else:
                global messages
                for record in records:
                    #TODO: optimise....
                    #message = json.loads(json.dumps(json.loads(record.value()), indent=4))
                    message = json.loads(record.value())
                    messages.append(message) 
                    #print(message)
        
    except Exception as e:
        print("Exception in getNewTweets: " + str(e))
        logging.warning("Exception in getNewTweets: " + str(e))
        consumer.close()

   



def streamToTweetCountsObjectsList(passedData):
    result = []
    for entry in passedData:
        result.append(TweetCounts(
            entry["ID"],
            entry["RETWEETCOUNT"],
            entry["FAVORITECOUNT"],
            entry["CREATEDAT"]
        ))

    return result

def listToTweetCountObjectsList(passedMessages):
    result = []
    for message in passedMessages:
        result.append(TweetCounts(
            message[0], message[1], message[2]
        ))

    return result

def reformatToStrIdBatches(pt):

    if len(pt) == 0:
        return None

    result = []

    if len(pt) > NUMBER_OF_TWEETS_API_CAN_HANDLE:       
        while len(pt) > NUMBER_OF_TWEETS_API_CAN_HANDLE:
            result.append(reformatMessagesToIdsString(pt[:NUMBER_OF_TWEETS_API_CAN_HANDLE]))
            pt = pt[NUMBER_OF_TWEETS_API_CAN_HANDLE:]

    if len(pt) > 0:
        result.append(reformatMessagesToIdsString(pt))

    return result
    
         

def reformatMessagesToIdsString(messagesArray):
    return ",".join([str(message["ID"]) for message in messagesArray[:NUMBER_OF_TWEETS_API_CAN_HANDLE]])

def idsToString(tweetsList, limitation):
    result = []
    
    while len(tweetsList) >= limitation:
        result.append(",".join([str(tweetData.id) for tweetData in tweetsList[:limitation]]))
        tweetsList = tweetsList[limitation:]

    if len(tweetsList) > 0:
        result.append(",".join([str(tweetData.id) for tweetData in tweetsList]))
    
    return result

def createBatches():
    pass


def updateNewTweets(batchesNum, batchSize):
    global NEW_TWEETS_TABLE
    global TRENDING_TWEETS_TABLE
    global TRENDING_THRESHOLD 
    global NUMBER_OF_TWEETS_API_CAN_HANDLE

    print("[1.] Starting: update NEW tweets ---") 
    logging.warning("[1.] Starting: update NEW tweets ---")
    

    # # Format messages to TweetCounts objects
    # formattedNewTweets = streamToTweetCountsObjectsList(messages)

    

    # Get latest tweets from "new" table (according to limits)
    pt = getTweets(NEW_TWEETS_TABLE, batchesNum, batchSize)

    print("Total number of tweets from NEW table: " + str(len(pt)))  
    logging.warning("Total number of tweets from NEW table: " + str(len(pt)))

    if len(pt) == 0:
        print("Ignoring the rest of operations")
        logging.warning("Ignoring the rest of operations")
        return

    formattedExistingTweets = listToTweetCountObjectsList(pt)

    # TODO: thing about limitations
    # if len(pt) < (batchesNum * batchSize) and len(messages) > 0:
    #     pt.extend(messages[:(batchesNum * batchSize) - len(pt)])

    #formattedExistingTweets.extend(formattedNewTweets)
    
    # Format tweets to string batches
    strBatches = idsToString(formattedExistingTweets, NUMBER_OF_TWEETS_API_CAN_HANDLE)
    
    # TODO: maybe if left, instead of deleteing store somewhere?
    pt.clear()
    #formattedNewTweets.clear()
    formattedExistingTweets.clear()

    
    # print(len(strBatches))
    # if len(strBatches) == 0:
    #     print("0 messages to process. Ignoring remaining steps.")
    #     return

    # Get update information of tweets
    ut = callApi(strBatches)
  

    # Store trending tweets in db
    storeTweets(TRENDING_TWEETS_TABLE, ut, TRENDING_THRESHOLD)

    # Delete already checked tweets from db (sort of?)
    deleteTweets(NEW_TWEETS_TABLE, batchesNum, batchSize)

    strBatches.clear()
    ut.clear()
    


def storeStreamTweets(batchesNum, batchSize):
    global messages

    print("[2.] Starting: store NEWest tweets ---")
    logging.warning("[2.] Starting: store NEWest tweets ---") 

    # Format messages to TweetCounts objects
    formattedNewTweets = streamToTweetCountsObjectsList(messages)

    if len(formattedNewTweets) == 0:
        print("Nothing to store, moving on")
        logging.warning("Nothing to store, moving on") 
        return
        
    storeNewestTweets(NEW_TWEETS_TABLE, formattedNewTweets)
    #storeTweets(NEW_TWEETS_TABLE, formattedNewTweets, 0)

    formattedNewTweets.clear()
    messages.clear()

def updateTrendingTweets(batchesNum, batchSize):
    global NEW_TWEETS_TABLE
    global TRENDING_TWEETS_TABLE
    global TRENDING_THRESHOLD 

    print("[3.] Starting: update TRENDING tweets ---") 
    logging.warning("[3.] Starting: update TRENDING tweets ---")  

    # # Get trending tweets (according to limits)
    # tn = getTrendingTweetsFromNew(NEW_TWEETS_TABLE, batchesNum, batchSize, TRENDING_THRESHOLD)
    # print("Total number of tweets above threshold: " + str(len(tn)))  

    # formattedNewTrendingTweets = listToTweetCountObjectsList(tn)

    # Get latest tweets from "new" table (according to limits)
    tt = getTweets(TRENDING_TWEETS_TABLE, batchesNum, batchSize)

    print("Total number of tweets from TRENDING table: " + str(len(tt)))  
    logging.warning("Total number of tweets from TRENDING table: " + str(len(tt)))  
    if len(tt) == 0:
        print("Ignoring the rest of operations")
        logging.warning("Ignoring the rest of operations")  
        return

    formattedTrendingTweets = listToTweetCountObjectsList(tt)

    tt.clear()

    # formattedTrendingTweets.extend(formattedNewTrendingTweets)

    # Format tweets to string batches
    strBatches = idsToString(formattedTrendingTweets, NUMBER_OF_TWEETS_API_CAN_HANDLE)
    
    # tn.clear()

    #TODO: check below
    # Reorder tweets (because get works from top)
    #reorderTrending(TRENDING_TWEETS_TABLE, batchesNum, batchSize, TRENDING_THRESHOLD)

    # Get update information of tweets
    ut = callApi(strBatches) 

    # Store trending tweets in db
    storeTweets(TRENDING_TWEETS_TABLE, ut, TRENDING_THRESHOLD)

    ut.clear()
    strBatches.clear()


async def updatingAllTweets(BATCHES_LIMIT, BATCH_SIZE):
    updateNewTweets(BATCHES_LIMIT, BATCH_SIZE)
    storeStreamTweets(BATCHES_LIMIT, BATCH_SIZE)
    updateTrendingTweets(BATCHES_LIMIT, BATCH_SIZE)


async def main():

    # Set up place to poll data from
    """
    consumer = Consumer({
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'my-consumer-1',
        'auto.offset.reset': 'latest'
    })
    """
    
    consumer = Consumer({
        'bootstrap.servers': 'broker:29092',
        'group.id': 'my-consumer-1',
        'auto.offset.reset': 'latest'
    })
    
    consumer.subscribe(['tweets_to_analyse_01'])

    counter = 0

    try:
        while True:
            print("----- Loop Begins -----")
            logging.warning("Loop Beginsw")
            await getNewTweets(consumer)
            await updatingAllTweets(BATCHES_LIMIT, BATCH_SIZE)
            counter += 1
            print("Round: " + str(counter))
            #taskGettingNewTweets = asyncio.create_task(getNewTweets())
            #taskUpdatingAllTweets = asyncio.create_task(updatingAllTweets(BATCHES_LIMIT, BATCH_SIZE))

            #await asyncio.gather(taskGettingNewTweets)
            print("--- End of loop (sleep) ---")
            time.sleep(5)

    except Exception as e:
        print(str(e))
        logging.warning(str(e))
        consumer.close()
    

asyncio.run(main())
