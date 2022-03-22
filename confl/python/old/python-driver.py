from operator import add
import time
import sys
import traceback
import logging
import json
from confluent_kafka import Consumer

from TweetCounts import TweetCounts
from get_tweets_with_bearer_token import createCallToApi, createCallToApiTrending
from python_to_mysql_move import checkIfSomethingToMove
from python_to_mysql_move import deleteNotPopular

# TODO: check these values
POLL_TIME = 1 # might be good, not sure. Might need to be increased
SLEEP_TIME = 10 # later: 600sec - 10min
NUMBER_API_CAN_HANDLE = 2 # Set to 100, because API can query that much
THRESHOLD_OF_INTEREST = 1 # set to 100 (or 1000)


consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my-consumer-1',
    'auto.offset.reset': 'earliest'
})
consumer.subscribe(['tweets_to_analyse_01'])


# def exportToApiCall(idsToCall):
#     # convert int to str
#     converted_list = [str(element) for element in idsToCall]

#     # create format "ids=121,456, 54.."
#     combine_ids = "ids=" + ",".join(converted_list)

#     # call function and store data for new tweets
#     createCallToApi(combine_ids, "tweet_counts")

    



def main():

    idsToExport = []
    stringBatchesForCalls = []
    stringOfExisting = []

    while True:
        try:
            callApi = False
            print("Running loop with poll time=" + str(POLL_TIME) + ", s sleep time= " + str(SLEEP_TIME) + " s")
            message = consumer.poll(POLL_TIME)

            
                
            if not message:

                # Update existing tweets in tweet_count
                print("Number of existing batches: " + str(len(stringOfExisting)))
                createCallToApi(stringOfExisting, "tweet_counts")
                del stringOfExisting

                # Check if any of existing new tweets are trending and move to trending
                checkIfSomethingToMove(THRESHOLD_OF_INTEREST)

                # Delete less popular (remaining)
                deleteNotPopular()

                
                stringOfExisting = stringBatchesForCalls.copy()

                if callApi:
                    print("Number of batches for api call: " + str(len(stringBatchesForCalls)))
                    createCallToApi(stringBatchesForCalls, "tweet_counts")
                    stringBatchesForCalls = []
                    

                # update trending
                createCallToApiTrending("trending_tweet_counts", NUMBER_API_CAN_HANDLE)

                print("Sleep")
                time.sleep(SLEEP_TIME) # Sleep for 10 seconds now
                    
            if message is not None:
                print(f"Received message: {message.value().decode('utf-8')}")
                
                idsToExport.append(json.loads(message.value())["ID"])

           
                print("idsToExport before while" + str(idsToExport))
                while len(idsToExport) > NUMBER_API_CAN_HANDLE:
                    callApi = True
                    # convert int to str
                    converted_list = ",".join([str(element) for element in idsToExport[:NUMBER_API_CAN_HANDLE]])
                    stringBatchesForCalls.append(converted_list)
                    idsToExport = idsToExport[NUMBER_API_CAN_HANDLE:]
                
                print("idsToExport after while" + str(idsToExport))
                continue
            # while len(idsToExport) > 0:

            #     callApi = False

            #     # Export new tweets to track
            #     if len(idsToExport) > NUMBER_API_CAN_HANDLE:

            #         callApi = True

            #         # convert int to str
            #         converted_list = ",".join([str(element) for element in idsToExport[:NUMBER_API_CAN_HANDLE]])
            #         stringBatchesForCalls.append(converted_list)
            #         idsToExport = idsToExport[NUMBER_API_CAN_HANDLE:]
            #     else:
            #         pass
            #         #converted_list = ",".join([str(element) for element in idsToExport[:NUMBER_API_CAN_HANDLE]])
            #         #stringBatchesForCalls.append(converted_list)
            #         #idsToExport = []
                    
            

           

                
            
        except Exception as e:
            print("Except loop")
            logging.error(traceback.format_exc())
            # Handle any exception here
            sys.exit()
        finally:
            print("Finally loop")




main()
