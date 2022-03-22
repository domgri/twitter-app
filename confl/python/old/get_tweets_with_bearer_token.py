import imp
import requests
import os
import json

from TweetCounts import TweetCounts

from python_to_mysql_table import storeToMySqlDB;
from python_to_mysql_move import getTrendingStringArray;

# To set your enviornment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
# bearer_token = os.environ.get("BEARER_TOKEN")

bearer_token = "AAAAAAAAAAAAAAAAAAAAAIKJZgEAAAAAl4wx6SGi%2BwWlqcKGwb%2BFwd5gfLQ%3D7tFzIrWvF5oZMPajKjTgJQJVtMMQZrwsXCTmLUR8tSYHQBKY9X"


def create_url(idsString):
    tweet_fields = "tweet.fields=public_metrics"
    # Tweet fields are adjustable.
    # Options include:
    # attachments, author_id, context_annotations,
    # conversation_id, created_at, entities, geo, id,
    # in_reply_to_user_id, lang, non_public_metrics, organic_metrics,
    # possibly_sensitive, promoted_metrics, public_metrics, referenced_tweets,
    # source, text, and withheld
    #ids = "ids=1498318595167764480,1498318579564953603"
    # You can adjust ids to include a single Tweets.
    # Or you can add to up to 100 comma-separated IDs
    #url = "https://api.twitter.com/2/tweets?{}&{}".format(ids, tweet_fields)
    url = "https://api.twitter.com/2/tweets?{}&{}".format(idsString, tweet_fields)
    return url


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2TweetLookupPython"
    return r


def connect_to_endpoint(url):
    response = requests.request("GET", url, auth=bearer_oauth)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()


def createCallToApiTrending(tableToStore, NUMBER_API_CAN_HANDLE):
    stringbatchesToCall = getTrendingStringArray(tableToStore, NUMBER_API_CAN_HANDLE)
    createCallToApi(stringbatchesToCall, tableToStore)

def createCallToApi(stringbatchesToCall, tableToStore):

    for batch in stringbatchesToCall:
        
        # create url and connect
        url = create_url("ids=" + str(batch))
        json_response = connect_to_endpoint(url)

        # format response
        json_object = json.loads(json.dumps(json_response, indent=4))

        exportData = []
        for entry in json_object["data"]:
            exportData.append(TweetCounts(
                entry["id"],
                entry["public_metrics"]["retweet_count"],
                entry["public_metrics"]["like_count"]
            ))
        
        storeToMySqlDB(exportData, tableToStore)
        del exportData
    

        

    #print(json.dumps(json_response, indent=4)["data"])


if __name__ == "__main__":
    createCallToApi()
