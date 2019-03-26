Source: https://github.com/vkorukanti/spark-docker-compose

# Docker compose for spawning on demand HDFS and Spark clusters

# Build the required Docker images
## Spark Image
`docker build -t hadoop-spark ./hadoop-spark/`

## Namenode
`docker build -t hdfs-namenode ./hdfs-namenode/`
## DataNode
`docker build -t hdfs-datanode ./hdfs-datanode/`

##Spark-Master
`docker build -t spark-master ./spark-master/`

## Spark-Slave
`docker build -t spark-slave ./spark-slave/`

# Run the cluster
Note: Run below commands from the directory where `docker-compose.yml` file is present.
## bring up the cluster
`docker-compose up -d`
## stop the cluster
`docker-compose stop`
## restart the stopped cluster
`docker-compose start`
## remove containers
`docker-compose rm -f`
## to scale HDFS datanode or Spark worker containers
`docker-compose scale spark-slave=n` where n is the new number of containers.
