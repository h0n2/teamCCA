#!/bin/bash

# Start the SSH daemon
service ssh restart

# Setup password less ssh
sshpass -p screencast ssh-copy-id root@localhost

sed -i "s#localhost#$NAMENODE_HOSTNAME#g" /opt/hadoop-2.9.0/etc/hadoop/core-site.xml

# Start spark master and worker services
start-master.sh
start-slave.sh spark://`hostname`:7077

# Run in daemon mode, don't exit
while true; do
  sleep 100;
done
