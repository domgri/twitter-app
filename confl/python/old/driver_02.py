import asyncio
import json
from textwrap import indent
import time
import threading 
from collections import deque
from confluent_kafka import Consumer
from mysql_function import getTweets, getTrendingTweetsFromNew, deleteTweets, storeTweets, reorderTrending
from twitter_api_functions import callApi
from TweetCounts import TweetCounts


#TODO: TEST FUNCTION BY FUNCTION AND MAKE ASYNCHRONOUS

MAX_NUMBER_OF_TWEETS_TO_CONSUME = 5
NUMBER_OF_TWEETS_API_CAN_HANDLE = 2 # 100
NEW_TWEETS_TABLE = "new_tweets"
TRENDING_TWEETS_TABLE = "trending_tweets"
BATCHES_LIMIT = 9
BATCH_SIZE = 2
TRENDING_THRESHOLD = 1

messages = []
newBatches = deque()

async def getNewTweets():

    timespan = 10 # 10s
    timeout = time.time() + timespan 

    print("Starting new tweets fetch for " + str(timespan) + " seconds")   

    try:
        # Set up place to poll data from
        consumer = Consumer({
            'bootstrap.servers': 'localhost:9092',
            'group.id': 'my-consumer-1',
            'auto.offset.reset': 'earliest'
        })
        consumer.subscribe(['tweets_to_analyse_01'])
        while time.time() < timeout:
             
            records = consumer.consume(timeout=timespan, num_messages=MAX_NUMBER_OF_TWEETS_TO_CONSUME)

            if not records:
                #print("Nothing to consume, sleeping (for " + str(timespan/10) +" seconds)")
                #time.sleep(timespan/10)
                print("0 records consumed")
            else:
                global messages
                for record in records:
                    #TODO: optimise....
                    #message = json.loads(json.dumps(json.loads(record.value()), indent=4))
                    message = json.loads(record.value())
                    messages.append(message) 
                    print(message)
    except Exception as e:
        print("Exception in getNewTweets: " + str(e))
        consumer.close()


def streamToTweetCountsObjectsList(passedData):
    result = []
    for entry in passedData:
        result.append(TweetCounts(
            entry["ID"],
            entry["RETWEETCOUNT"],
            entry["FAVORITECOUNT"]
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

# def formatTweets(tweetsList, limitation):
#     result = []
#     # while len(tweetsData) > NUMBER_OF_TWEETS_API_CAN_HANDLE:
#     #     result.append(",".join([str(tweetData) for tweetData in tweetsData[:NUMBER_OF_TWEETS_API_CAN_HANDLE]]))
#     #     tweetsData = tweetsData[NUMBER_OF_TWEETS_API_CAN_HANDLE:]

#     # if len(tweetsData) > 0:
#     #     result.append(",".join([str(tweetData) for tweetData in tweetsData]))

#     while len(tweetsList) >= limitation:
#         result.append(",".join([str(tweetData.id) for tweetData in tweetsList[:limitation]]))
#         tweetsList = tweetsList[limitation:]

#     print(tweetsList)

#     for a  in tweetsList:
#         print(a)
#         print(a.id)
#         break
#     if len(tweetsList) > 0:
#         result.append(",".join([str(tweetData.id) for tweetData in tweetsList]))
    
#     return result

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
    global messages

    print("Starting update NEW tweets") 

    # Format messages to TweetCounts objects
    formattedNewTweets = streamToTweetCountsObjectsList(messages)

    # Get latest tweets from "new" table (according to limits)
    pt = getTweets(NEW_TWEETS_TABLE, batchesNum, batchSize)

    print("Total number of tweets from NEW table: " + str(len(pt)))  

    formattedExistingTweets = listToTweetCountObjectsList(pt)

    # TODO: thing about limitations
    # if len(pt) < (batchesNum * batchSize) and len(messages) > 0:
    #     pt.extend(messages[:(batchesNum * batchSize) - len(pt)])

    formattedExistingTweets.extend(formattedNewTweets)
    
    # Format tweets to string batches
    strBatches = idsToString(formattedExistingTweets, NUMBER_OF_TWEETS_API_CAN_HANDLE)
    print(strBatches)
    
    # TODO: maybe if left, instead of deleteing store somewhere?
    pt.clear()
    formattedNewTweets.clear()
    formattedExistingTweets.clear()

    
    print(len(strBatches))
    if len(strBatches) == 0:
        print("0 messages to process. Ignoring remaining steps.")
        return

    # Get update information of tweets
    print("String batches:" + str(strBatches))
    ut = callApi(strBatches)

    # # Delete those tweets from db
    # #deleteTweets(NEW_TWEETS_TABLE, batchesNum, batchSize)

    # Store trending tweets in db
    storeTweets(NEW_TWEETS_TABLE, ut, 0)
    ut.clear()
    strBatches.clear()

def updateTrendingTweets(BatchesNum, BatchSize):
    global NEW_TWEETS_TABLE
    global TRENDING_TWEETS_TABLE
    global TRENDING_THRESHOLD 
    global messages

    print("Starting update TRENDING tweets")  

    # Get trending tweets (according to limits)
    tt = getTrendingTweetsFromNew(NEW_TWEETS_TABLE, BatchesNum, BatchSize, TRENDING_THRESHOLD)
    print("Total number of tweets: " + str(len(tt)))  

    # Format tweets to string batches
    ptStrBatches = formatTweets(tt)
    tt.clear()

    # Reorder tweets (because get works from top)
    reorderTrending(TRENDING_TWEETS_TABLE, BatchesNum, BatchSize, TRENDING_THRESHOLD)

    # Get update information of tweets
    ut = callApi(ptStrBatches)
    print("Number of tweets should be updated: " + str(len(ut)))  

    # Store trending tweets in db
    storeTweets(TRENDING_TWEETS_TABLE, ut, TRENDING_THRESHOLD)




async def updatingAllTweets(BATCHES_LIMIT, BATCH_SIZE):
    updateNewTweets(BATCHES_LIMIT, BATCH_SIZE)
    #updateTrendingTweets(BATCHES_LIMIT, BATCH_SIZE)


async def main():

    while True:
        print("--- Loop Begins ---")
        await getNewTweets()
        await updatingAllTweets(BATCHES_LIMIT, BATCH_SIZE)
        #taskGettingNewTweets = asyncio.create_task(getNewTweets())
        #taskUpdatingAllTweets = asyncio.create_task(updatingAllTweets(BATCHES_LIMIT, BATCH_SIZE))

        #await asyncio.gather(taskGettingNewTweets)



asyncio.run(main())