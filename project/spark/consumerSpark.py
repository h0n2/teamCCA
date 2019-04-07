import os
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.3.1 pyspark-shell py2neo'

from pip._internal import main as pipmain 
pipmain(['install','py2neo'])


from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import json
import PreparePub

sc = SparkContext(appName="AminerKafkaSpark")
ssc = StreamingContext(sc,10)

#Defining Kafka Consumer
kafkaStream = KafkaUtils.createStream(ssc,'zookeeper:2181','spark-streaming1',{'foobar':1})
#kafkaStream = KafkaUtils.createStream(ssc,'broker:19092','spark-streaming1',{'foobar':1})
#Extract the content

# for line in kafkaStream:
#     parsed1 = json.loads[line[1]]
#     print(type(line))
#     line.pprint(num=1)
#     print(type(parsed1))
#     parsed1.pprint(num=3)


# print("******************************************************************************************")



lines = kafkaStream.map(lambda x:x[1])

lrd = lines.map(lambda p: PreparePub.formatNodes(p[1]))

lines.pprint()

#PreparePub.formatNodes(lines)
# counts = lines.flatMap(lambda line: line.split(" ")) \
#                   .map(lambda word: (word, 1)) \
#                   .reduceByKey(lambda a, b: a+b)
# counts.pprint()

# #parsed = kafkaStream.map(lambda v:json.loads(v[1]))  
# print("**************************************END****************************************************")

#parsed = kafkaStream.map(lambda v:json.loads(v[1])) 
#authors_dstream = parsed.map(lambda page: page['title'])


#parsed.pprint(num=3)

# lines = ssc.socketTextStream("zookeeper",2181)
# words = lines.flatMap(lambda line: line.split(" "))
# # Count each word in each batch
# pairs = words.map(lambda word: (word, 1))
# wordCounts = pairs.reduceByKey(lambda x, y: x + y)

# # Print the first ten elements of each RDD generated in this DStream to the console
# wordCounts.pprint()

#PreparePub.formatNodes(parsed)

ssc.start()
ssc.awaitTermination()



#pageids = parsed.map(lambda paper: paper['id'])


