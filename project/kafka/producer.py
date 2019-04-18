#  Core Kafka Producer script for generating the Messages
#  Authored: hcwong2@illinois.edu, manaskm2@illinois.edu, fmc2@illinois.edu, skusuma3@illinois.edu

#from pip._internal import main as pipmain
#pipmain(['install','kafka-python'])


from kafka import KafkaProducer
import time
import json
import os


folder = r"data/"
producer = KafkaProducer(bootstrap_servers='localhost:9092', request_timeout_ms=1000000, api_version_auto_timeout_ms=1000000)
files = filter(lambda  x: x[-4:] == '.txt', os.listdir(folder))
#filename = r"data\aminer_papers_0.txt"
cnt =0
for filename in files:
    with open((folder + filename), encoding="UTF-8") as json_file:
        for line_number, line in enumerate(json_file):
            #if line_number <= 100:
                if cnt >=5:
                    print("sleeping ...")
                    time.sleep(15)
                    cnt = 0
                else:
                    # Load the Json and construct the new json
                    jsonObj = json.loads(line)
                    try:
                        del jsonObj['abstract']
                        newLine = json.dumps(jsonObj)
                    except KeyError:
                        newLine = line

                    print(newLine)
                    producer.send('aminer', bytes(newLine,'utf-8'))
                    cnt = cnt + 1

        os.rename((folder + filename), (folder + filename[:-4]+'.prs'))
        #else:
        #    break

#i=0
#while i <= 1000:
#    i += 1
#    producer.send('foobar',bytes("This is a very long test!",'utf-8'))