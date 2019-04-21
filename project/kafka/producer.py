#  Core Kafka Producer script for generating the Messages
#  Authored: hcwong2@illinois.edu, manaskm2@illinois.edu, fmc2@illinois.edu, skusuma3@illinois.edu

#from pip._internal import main as pipmain
#pipmain(['install','kafka-python'])


from pip._internal import main as pipmain 
pipmain(['install','kafka-python'])

from kafka import KafkaProducer
import time
import json
import os


folder = r"data/"
producer = KafkaProducer(bootstrap_servers='localhost:9092', request_timeout_ms=1000000, api_version_auto_timeout_ms=1000000)
files = filter(lambda  x: x[-4:] == '.txt', os.listdir(folder))
#filename = r"data\aminer_papers_0.txt"
batchSize = 1000
cnt=0
for filename in files:
    with open((folder + filename), encoding="UTF-8") as json_file:
        print('### Processing starts for',filename,'###')
        for line_number, line in enumerate(json_file):
            if cnt > batchSize:
                print("Waiting to send next batch...")
                time.sleep(5)
                cnt = 0
            
            # Load the Json and construct the new json
            jsonObj = json.loads(line)
            try:
                del jsonObj['abstract']
                newLine = json.dumps(jsonObj)
            except KeyError:
                newLine = line

            print(str(line_number),newLine)
            producer.send('aminer', bytes(newLine,'utf-8'))
            cnt = cnt + 1

        print('### Processing completed for',filename,'###')
        os.rename((folder + filename), (folder + filename[:-4]+'.prs'))
        time.sleep(5)

producer.close()