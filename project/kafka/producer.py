from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers='localhost:9092')
filename = r"data\aminer_papers_0.txt"

with open(filename, encoding="UTF-8") as json_file:
    for line_number, line in enumerate(json_file):
        producer.send('foobar', bytes(line,'utf-8'))