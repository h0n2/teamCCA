#Team30 Project LeCloud

## Run the cluster ( Playaround with Docker Compose)
Note: Run below commands from the directory where docker-compose.yml file is present.
### bring up the cluster in disconnected mode
```
docker-compose up -d
```
### stop the cluster
```
docker-compose stop
```
### restart the stopped cluster
```
docker-compose start
```
### remove containers
```
docker-compose rm -f
```

## Running Instructions
a. Load docker Images from docker-compose file
```
docker-compose up
or 
docker-compose up -d
```

b. Producer Code: 
( make sure file exists: project\kafka\data\aminer_papers_0.txt)

```python
python project\kafka\producer.py
```

c. Consumer Code: 
    Just before running the consumer, run the producer, so that messages are published to Kakfa Queue

  1. Simple Consumer Test: Connect to Spark Master docker and run 
  ```python
  python /opt/spark/code/consumer.py
  ```

  2. Spark Streaming Consumer: 
  ```python
  docker exec spark-master bin/spark-submit --verbose --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.3.1 --master spark://spark-master:7077 /opt/spark/code/consumerSpark.py
  ```

d.  Visualization:
    
    Connect to Neo4j browser using http://localhost:7474/browser with username: neo4j and password: password

```
Happy Learning Kafka ( Producer, Consumer), Spark-Streaming, Neo4j and binding docker images enables scaling for distributed processing
```

## Link to the Paper Published: TBD