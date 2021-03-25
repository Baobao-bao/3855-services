import connexion 
from connexion import NoContent
from swagger_ui_bundle import swagger_ui_path
from pykafka import KafkaClient 
from pykafka.common import OffsetType 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
import logging
import logging.config
import yaml
import json



base_url= "c:/Users/Bao/Desktop/3855/Audit/"

with open(base_url + "app_conf.yml", "r") as f:
    app_config = yaml.safe_load(f.read())

logger = logging.getLogger("basicLogger")
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)

DB_ENGINE = create_engine(f'mysql+pymysql://{app_config["datastore"]["user"]}:'f'{app_config["datastore"]["password"]}@{app_config["datastore"]["hostname"]}:'f'{app_config["datastore"]["port"]}/{app_config["datastore"]["db"]}')
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

def get_stock_news_reading(index):

    hostname = "%s:%d" % (app_config["events"]["hostname"],
    app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
    consumer_timeout_ms=1000)
    logger.info("Retrieving news at index %d" % index)

    count = 0
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            payload = msg["payload"]
            
            # Find the event at the index you want and
            if msg["type"] == "sn":

                if count == index:
                    event = payload
                    # return code 200
                    return event, 200
                count = count + 1
    except:
        logger.error("No more messages found")

        logger.error("Could not find news at index %d" % index)
    return { "message": "Not Found"}, 404

def get_stock_open_price_reading(index):

    hostname = "%s:%d" % (app_config["events"]["hostname"],
    app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
    consumer_timeout_ms=1000)
    logger.info("Retrieving open price at index %d" % index)

    count = 0
    print(index)
    print(type(index))
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            payload = msg["payload"]
            # Find the event at the index you want and
            if msg["type"] == "sn":

                if count == index:
                    event = payload
                    return event, 200
                count = count + 1
    except:
        logger.error("No more messages found")

        logger.error("Could not find open price at index %d" % index)
    return { "message": "Not Found"}, 404

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml",strict_validation=True,validate_responses=True)


if __name__ == "__main__":
    app.run(port=8110,debug=True)