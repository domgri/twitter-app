import asyncio
import json
from textwrap import indent
import time
import threading 
from collections import deque
from confluent_kafka import Consumer
from mysql_function import getTweets, deleteTweets, storeTweets, reorderTrending
from twitter_api_functions import callApi


#TODO: TEST FUNCTION BY FUNCTION AND MAKE ASYNCHRONOUS

NUMBER_OF_TWEETS_TO_CONSUME = 5
NUMBER_OF_TWEETS_API_CAN_HANDLE = 2 # 100
NEW_TWEETS_TABLE = "new_tweets"
TRENDING_TWEETS_TABLE = "trending_tweets"
BATCHES_LIMIT = 9
BATCH_SIZE = 2
TRENDING_THRESHOLD = 1

messages = []
newBatches = deque()

def getNewTweets():

    try:
         # Set up place to poll data from
        consumer = Consumer({
            'bootstrap.servers': 'localhost:9092',
            'group.id': 'my-consumer-1',
            'auto.offset.reset': 'earliest'
        })
        consumer.subscribe(['tweets_to_analyse_01'])
        while True:
            records = consumer.consume(timeout=5, num_messages=NUMBER_OF_TWEETS_TO_CONSUME)

            if not records:
                print("Sleep")
                time.sleep(10)
            else:
                global messages
                for record in records:
                    #TODO: optimise....
                    message = json.loads(json.dumps(json.loads(record.value()), indent=4))
                    messages.append(message) 
                    print(message)
    except Exception as e:
        print(e)
        consumer.close()

         
# https://stackoverflow.com/questions/50757497/simplest-async-await-example-possible-in-python
async def sleep():
    await asyncio.sleep(1)

def reformatMessagesToIdsString(messagesArray):
    return ",".join([str(message["ID"]) for message in messagesArray[:NUMBER_OF_TWEETS_API_CAN_HANDLE]])

def formatTweets(tweetsData):
    result = []
    while len(tweetsData) > NUMBER_OF_TWEETS_API_CAN_HANDLE:
        result.append(",".join([str(tweetData) for tweetData in tweetsData[:NUMBER_OF_TWEETS_API_CAN_HANDLE]]))
        tweetsData = tweetsData[NUMBER_OF_TWEETS_API_CAN_HANDLE:]

    if len(tweetsData) > 0:
        result.append(",".join([str(tweetData) for tweetData in tweetsData]))
    
    return result

def createBatches():
    pass

# https://stackoverflow.com/questions/54311325/how-to-make-a-function-that-includes-a-for-loop-non-blocking
# def getUpdates():
#     global messages
#     global newBatches
    
#     # Prepare batches from new tweets
#     # newBatches.extend(reformatMessagesToIdsString(messages))

#     deleteNotPotencialFromDB(POTENTIAL_TWEETS_TABLE)


def updateNewTweets(batchesNum, batchSize):
    global NEW_TWEETS_TABLE
    global TRENDING_TWEETS_TABLE
    global TRENDING_THRESHOLD 

    # Get latest tweets from "new" table (according to limits)
    pt = getTweets(NEW_TWEETS_TABLE, batchesNum, batchSize)

    # Format tweets to string batches
    ptStrBatches = formatTweets(pt)
    pt.clear()

    # Delete those tweets from db
    deleteTweets(NEW_TWEETS_TABLE, batchesNum, batchSize)

    # Get update information of tweets
    ut = callApi(ptStrBatches)

    # Store trending tweets in db
    storeTweets(TRENDING_TWEETS_TABLE, ut, TRENDING_THRESHOLD)
    ut.clear()

def updateTrendingTweets(BatchesNum, BatchSize):
    # Get trending tweets (according to limits)
    tt = getTweets(NEW_TWEETS_TABLE, BatchesNum, BatchSize, TRENDING_THRESHOLD)

    # Format tweets to string batches
    ptStrBatches = formatTweets(tt)
    tt.clear()

    # Reorder tweets (because get works from top)
    reorderTrending(TRENDING_TWEETS_TABLE, BatchesNum, BatchSize)

    # Get update information of tweets
    ut = callApi(ptStrBatches)

    # Store trending tweets in db
    storeTweets(TRENDING_TWEETS_TABLE, ut, TRENDING_THRESHOLD)




    pass

def main():
   
    # TODO: make schedule asynchornous calls
    updateNewTweets(BATCHES_LIMIT, BATCH_SIZE)

    updateTrendingTweets(BATCHES_LIMIT, BATCH_SIZE)

    # Older than 24 h?
    #clearTrending()

    print("main")
    # call getUpdatesFrom here...
    # and only then go to permanent poll
    getNewTweets()
    print("main3")
    pass



main()