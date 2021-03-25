import connexion 
from connexion import NoContent
import json
from swagger_ui_bundle import swagger_ui_path
import threading
import yaml
import logging
import logging.config
import requests
import datetime
from pykafka import KafkaClient

with open('c:/Users/Bao/Desktop/3855/lab 2 -Receiver/app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('c:/Users/Bao/Desktop/3855/lab 2 -Receiver/log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)

MAX_EVENT = 10
EVENT_FILE = "events.json"

def limit_data():
    with open('c:/Users/Bao/Desktop/3855/lab 2 -Receiver/'+ EVENT_FILE,"r") as file:
        content = file.read()
        if len(content) == 0:
            print("hi")
            return []
        data = json.loads(content)
        if len(data) <= (MAX_EVENT - 1):
                return data
        else:
            del data[MAX_EVENT-1]
            return data

def read_stock_open_price(body):
    # data = limit_data()
    # data.insert(0,body)
    # with open('c:/Users/Bao/Desktop/3855/lab 2 -Receiver/'+EVENT_FILE,"w") as file:
    #     json.dump(data, file)
    date = body["date"]
    my_format = logging.Formatter(f'Stored event "eventstore1"  request with a unique id of {date}')
    handler.setFormatter(my_format)
    logger.info("starting to push a message.")

    # x = requests.post(app_config["eventstore1"]["url"], json = body, headers={'Content-type': 'application/json'})
    client = KafkaClient(hosts='services-3855.eastus.cloudapp.azure.com:9092')
    topic = client.topics[str.encode("events")] # "events"?
    producer = topic.get_sync_producer()

    msg = { 
        "type": "sp",
        "datetime" :datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),"payload": body 
    }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    my_format = logging.Formatter(f'Returned event "eventstore2" response (Id: {date}) with status 201')
    handler.setFormatter(my_format)
    logger.info("finished pushing the message.")

    return NoContent,201

def read_stock_news(body):
    # data = limit_data()
    # data.insert(0,body)
    # with open('c:/Users/Bao/Desktop/3855/lab 2 -Receiver/'+ EVENT_FILE,"w") as file:
    #     json.dump(data, file)
    date = body["date"]
    my_format = logging.Formatter(f'Stored event "eventstore1"  request with a unique id of {date}')
    handler.setFormatter(my_format)
    logger.info("starting to push a message.")

    # x = requests.post(app_config["eventstore2"]["url"], json = body, headers={'Content-type': 'application/json'})

    client = KafkaClient(hosts='services-3855.eastus.cloudapp.azure.com:9092')
    print(client)
    topic = client.topics[str.encode("events")]
    producer = topic.get_sync_producer()

    msg = { 
        "type": "sn",
        "datetime" :datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),"payload": body 
    }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    my_format = logging.Formatter(f'Returned event "eventstore2" response (Id: {date}) with status 201')
    handler.setFormatter(my_format)
    logger.info("finished pushing the message.")
    return NoContent,201




app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml",strict_validation=True,validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080,debug=True)

# localhost:8080/ui