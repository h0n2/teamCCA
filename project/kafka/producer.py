from kafka import KafkaProducer
import time
import json

producer = KafkaProducer(bootstrap_servers='localhost:9092', request_timeout_ms=1000000, api_version_auto_timeout_ms=1000000)
filename = r"data\aminer_papers_0.txt"
cnt =0
with open(filename, encoding="UTF-8") as json_file:
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
        #else:
        #    break

#i=0
#while i <= 1000:
#    i += 1
#    producer.send('foobar',bytes("This is a very long test!",'utf-8'))