#Team30 Project LeCloud

## Run the cluster
Note: Run below commands from the directory where docker-compose.yml file is present.
### bring up the cluster
docker-compose up -d
### stop the cluster
docker-compose stop
### restart the stopped cluster
docker-compose start
### remove containers
docker-compose rm -f
### to scale HDFS datanode or Spark worker containers
docker-compose scale spark-slave=n where n is the new number of containers.
