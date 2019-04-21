#  Sample Kafka Consumer Script for testing the Consumer functionality
#  Authored: hcwong2@illinois.edu, manaskm2@illinois.edu, fmc2@illinois.edu, skusuma3@illinois.edu

import os
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.3.1 pyspark-shell'

from pip._internal import main as pipmain 
pipmain(['install','py2neo', 'kafka-python'])

from kafka import KafkaConsumer
#consumer = KafkaConsumer('foobar')
#for msg in consumer:
#    print (msg)

#from kafka import KafkaConsumer

# To consume latest messages and auto-commit offsets
consumer = KafkaConsumer('aminer',
                          bootstrap_servers='broker:19092')
for message in consumer:
    # message value and key are raw bytes -- decode if necessary!
    # e.g., for unicode: `message.value.decode('utf-8')`
    print ("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                          message.offset, message.key,
                                          message.value))
