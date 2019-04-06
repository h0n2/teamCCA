from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import kafkaUtils
import json

sc = SparkContext(appName="AminerKafkaSpark")
scstrm = StreamingContext(sc,120)

#Defining Kafka Consumer
kafkaStream = kafkaUtils.createStream(scstrm,'localhost:2181','spark-streaming1',{'foobar':1})

#Extract the content
parsed = kafkaStream.map(lambda v:json.loads(v[1]))

pageids = parsed.map(lambda paper: paper['id'])

pageids.pprint(10)

return scstrm
