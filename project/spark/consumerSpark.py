import os
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.3.1 pyspark-shell'
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import json

sc = SparkContext(appName="AminerKafkaSpark")
scstrm = StreamingContext(sc,120)

#Defining Kafka Consumer
kafkaStream = KafkaUtils.createStream(scstrm,'localhost:2181','spark-streaming1',{'foobar':1})

#Extract the content
parsed = kafkaStream.map(lambda v:json.loads(v[1]))

pageids = parsed.map(lambda paper: paper['id'])

pageids.pprint(10)
