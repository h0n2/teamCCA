# Team30 Project LeCloud

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
cd project\kafka
python producer.py
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
    
    1. Run local http server
    ```python
       cd project\guide
       python http-server.py
    ```
    This will be running againist localhost:8081 port pointing to guide folder
    (Check) Try to navigate http://localhost:18001/AMiner.html

    

    2. Connect to Neo4j browser using http://localhost:7474/browser with username: neo4j and password: password
        This will load the above AMiner.html tutorial page by default after connecting
        OR
        run this code in the query window 
        ```
            play: http://localhost:18001/AMiner.html    
        ```
Notes: If you see that above port is being used and not able to launch above url, then you can change the port in project\guide\http-server.py and launch this from neo4j browser with above command ( play: http://localhost:<port>/AMiner.html ). If you want it automatic launch then you need to update docker\db\config\neo4j.conf and restart the container.
```
Happy Learning Kafka ( Producer, Consumer), Spark-Streaming, Neo4j and binding docker images enables scaling for distributed processing
```

## Link to the Paper Published: TBD