"""
#https://linuxhint.com/read_data_kafka_python/

# Import KafkaConsumer from Kafka library
from kafka import KafkaConsumer

# Import sys module
import sys

# Define server with port
bootstrap_servers = ['localhost:9092']

# Define topic name from where the message will recieve
topicName = 'TWEET_ID_AND_COUNTS_01'

# Initialize consumer variable
consumer = KafkaConsumer (topicName,bootstrap_servers =
   bootstrap_servers)


while True:
	print(str("Reading data from " + topicName))
	
	if len(consumer.msg) > 0:
		# Read and print message from consumer
		for msg in consumer:
			print("Topic Name=%s,Message=%s"%(msg.topic,msg.value))
			
		print("Reading finished")
		
	# Sleep in seconds
	time.sleep(60)

# Terminate the script
sys.exit()
"""

"""
from kafka import KafkaConsumer
from kafka import TopicPartition

TOPIC = "TWEET_ID_AND_COUNTS_01"
#producer = KafkaProducer()
#producer.send(TOPIC, b'data')
consumer = KafkaConsumer(
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    consumer_timeout_ms=10000,
    group_id="_confluent-ksql-default_query_CSAS_TWEET_ID_AND_COUNTS_01_3",
    enable_auto_commit=False,
    auto_commit_interval_ms=1000
)
#topic_partition = TopicPartition(TOPIC, 0)
#assigned_topic = [topic_partition]
#consumer.assign(assigned_topic)
print(consumer)
for message in consumer:
	print("%s key=%s value=%s" % (message.topic, message.key, message.value))
consumer.commit()
"""



"""
This one works but cannot implement timeouts neatly


from kafka import KafkaConsumer

import json 

# To consume latest messages and auto-commit offsets
consumer = KafkaConsumer('tweets_to_analyse_01',
                         group_id='consumers_group_01',
                         bootstrap_servers=['localhost:9092'], 
                         auto_offset_reset='earliest', enable_auto_commit=False, 
                         value_deserializer=lambda m: json.loads(m.decode('ascii')))

for message in consumer:
	print("2")
    # message value and key are raw bytes -- decode if necessary!
    # e.g., for unicode: `message.value.decode('utf-8')`
	print ("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                          message.offset, message.key,
                                          message.value))
print("3")

# consume earliest available messages, don't commit offsets
#KafkaConsumer(auto_offset_reset='earliest', enable_auto_commit=False)

# consume json messages
#KafkaConsumer(value_deserializer=lambda m: json.loads(m.decode('ascii')))

# consume msgpack
#KafkaConsumer(value_deserializer=msgpack.unpackb)

# StopIteration if no message after 1sec
#KafkaConsumer(consumer_timeout_ms=1000)

# Subscribe to a regex topic pattern
#consumer = KafkaConsumer()
#consumer.subscribe(pattern='^awesome.*')

# Use multiple consumers in parallel w/ 0.9 kafka brokers
# typically you would run each on a different server / process / CPU
#consumer1 = KafkaConsumer('my-topic',
#                          group_id='my-group',
#                          bootstrap_servers='my.server.com')
#consumer2 = KafkaConsumer('my-topic',
#                          group_id='my-group',
#                          bootstrap_servers='my.server.com')


"""

# https://stackoverflow.com/questions/61968794/what-is-the-best-practice-for-keeping-kafka-consumer-alive-in-python

import time
import sys
import traceback
import logging
import json
from confluent_kafka import Consumer

from TweetCounts import TweetCounts

POLL_TIME = 1
SLEEP_TIME = 10

dataToExport = []


consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my-consumer-1',
    'auto.offset.reset': 'earliest'
})
consumer.subscribe(['tweets_to_analyse_01'])

while True:
	try: 

		print("Running loop with poll time=" + str(POLL_TIME) + ", s sleep time= " + str(SLEEP_TIME) + " s")
		message = consumer.poll(POLL_TIME)
			
		if not message:
			print("Sleep")
			time.sleep(SLEEP_TIME) # Sleep for 10 seconds now
				
		if message is not None:
			print(f"Received message: {message.value().decode('utf-8')}")

			# dataToExport.append(TweetCounts(
			# 	json.loads(message.value())["ID"],
			# 	json.loads(message.value())["RETWEETCOUNT"],
			# 	json.loads(message.value())["FAVORITECOUNT"]
			# ))
 		
	except Exception as e:
		print("Except loop")
		logging.error(traceback.format_exc())
		# Handle any exception here
		sys.exit()
	finally:
		print("Finally loop")
		
		# Terminate the script
		
		#print("Goodbye")
		
consumer.close()
sys.exit()
