
import requests
import json
from collections import deque
from TweetCounts import TweetCounts


bearer_token = "AAAAAAAAAAAAAAAAAAAAAIKJZgEAAAAAl4wx6SGi%2BwWlqcKGwb%2BFwd5gfLQ%3D7tFzIrWvF5oZMPajKjTgJQJVtMMQZrwsXCTmLUR8tSYHQBKY9X"


def callApi(stringBatches):

    tweets = deque()
    for batch in stringBatches:
        
        # create url and connect
        url = create_url("ids=" + str(batch))
        json_response = connect_to_endpoint(url)

        # format response
        json_object = json.loads(json.dumps(json_response, indent=4))
        #print(json_object)

        for entry in json_object["data"]:
            tweets.append(TweetCounts(
                entry["id"],
                entry["public_metrics"]["retweet_count"],
                entry["public_metrics"]["like_count"]
            ))
    return tweets
        

def create_url(idsString):
    tweet_fields = "tweet.fields=public_metrics"
    url = "https://api.twitter.com/2/tweets?{}&{}".format(idsString, tweet_fields)
    return url



def connect_to_endpoint(url):
    response = requests.request("GET", url, auth=bearer_oauth)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2TweetLookupPython"
    return r