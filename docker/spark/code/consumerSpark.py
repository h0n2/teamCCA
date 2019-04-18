#  Core Kafka Consumer for consuming Kafka messages, integrating with Neo4j
#  Authored: hcwong2@illinois.edu, manaskm2@illinois.edu, fmc2@illinois.edu, skusuma3@illinois.edu

from __future__ import print_function

import os
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.3.1 pyspark-shell'

from pip._internal import main as pipmain 
pipmain(['install','py2neo', 'kafka-python'])

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import json
import PreparePub

sc = SparkContext(appName="AminerKafkaSpark")
ssc = StreamingContext(sc,10)  # 10 seconds 

#Defining Kafka Consumer
# consumer1 <- Consumer Instance(Consumer GroupID)
# foobar <- Topic
# 1 <- Per topic kafka partitions to consume
# Say for example you have a topic named "Topic1" with 2 partitions and you have provided the option 'Topic1':1, 
#  then Kafka receiver will read 1 partition at a time [It will eventually read all the partitions but will read one partition at a time]. 
#  The reason for this is to read the messages in partition and also preserving the order in which the data is written to the topic.

kafkaStream = KafkaUtils.createStream(ssc,'zookeeper:2181','consumer1',{'aminer':1})

def processRecord(record):
	#print(type(record))  #pyspark.rdd.RDD
	newRecord = record.collect()
	for x in newRecord:
		PreparePub.formatNodes(json.loads(x))
	print('******************COMPLETE********************')

lines = kafkaStream.map(lambda x:x[1])
lines.foreachRDD(processRecord)

ssc.start()
ssc.awaitTermination()
