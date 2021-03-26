import connexion 
from connexion import NoContent
from swagger_ui_bundle import swagger_ui_path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pykafka import KafkaClient 
from pykafka.common import OffsetType 

from base import Base
from stock_open_price import StockOpenPrice
from stock_news import StockNews
import datetime
import logging
import logging.config
import yaml
import json
from threading import Thread 


with open("app_conf.yml", "r") as f:
    app_config = yaml.safe_load(f.read())

with open("log_conf.yml", "r") as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)


logger = logging.getLogger("basicLogger")
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)



DB_ENGINE = create_engine(f'mysql+pymysql://{app_config["datastore"]["user"]}:'f'{app_config["datastore"]["password"]}@{app_config["datastore"]["hostname"]}:'f'{app_config["datastore"]["port"]}/{app_config["datastore"]["db"]}')
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

logger.info("Connecting to DB: Hostname:services-3855.eastus.cloudapp.azure.com, Port: 3306.")






def get_stock_price_readings(timestamp):
    """ Gets new stock price readings after the timestamp """
    session = DB_SESSION()

    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%d")
    print(timestamp_datetime)

    readings = session.query(StockOpenPrice).filter(StockOpenPrice.date >=
    timestamp_datetime)
    results_list = []

    for reading in readings:
        results_list.append(reading.to_dict())
    session.close()

    logger.info("Query for stock price readings after %s returns %d results" %(timestamp, len(results_list)))

    return results_list, 200


def get_stock_news_readings(timestamp):
    """ Gets new stock news readings after the timestamp """
    session = DB_SESSION()

    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%d")
    print(timestamp_datetime)

    readings = session.query(StockNews).filter(StockNews.date >=
    timestamp_datetime) 
    results_list = []
    
    for reading in readings:
        results_list.append(reading.to_dict())
    session.close()

    logger.info("Query for Stock News readings after %s returns %d results" %(timestamp, len(results_list)))

    return results_list, 200


def process_messages():
    """ Process event messages """
    print("hi")
    
    hostname = "%s:%d" % (app_config["events"]["hostname"],app_config["events"]["port"])
    print(hostname)
    client = KafkaClient(hosts=hostname)
    logger.info(client)
    print(client) 

    topic = client.topics[str.encode(app_config["events"]["topic"])]
    print(topic)
    # Create a consume on a consumer group, that only reads new messages
    # (uncommitted messages) when the service re-starts (i.e., it doesn't
    # read all the old messages from the history in the message queue).
    consumer = topic.get_simple_consumer(
        consumer_group=b'event_group',
        reset_offset_on_start=False,
        auto_offset_reset=OffsetType.LATEST
    )
    print(consumer)
    # This is blocking - it will wait for a new message
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)
        payload = msg["payload"]
        print("payload",payload)
        if msg["type"] == "sp": # Change this to your event type
            # Store the event1 (i.e., the payload) to the DB

            session = DB_SESSION()

            open_price = StockOpenPrice(
                                payload['stock_code'],
                                payload['open_price'],
                                datetime.datetime.strptime(payload["date"][0:10], '%Y-%m-%d'),)

            session.add(open_price)

            session.commit()
            session.close()

            date = payload["date"]
            my_format = logging.Formatter(f'Stored event "eventstore1"  request with a unique id of {date}')
            handler.setFormatter(my_format)
            logger.info("finished storing stock open price to database.")


        elif msg["type"] == "sn": # Change this to your event type
            # Store the event2 (i.e., the payload) to the DB
            session = DB_SESSION()

            stock_news = StockNews(
                        payload['stock_code'],
                        payload['news'],
                        payload['source'],
                        datetime.datetime.strptime(payload["date"][0:10], '%Y-%m-%d'))

            session.add(stock_news)

            session.commit()
            session.close()


            date = payload["date"]
            my_format = logging.Formatter(f'Stored event "eventstore2"  request with a unique id of {date}')
            handler.setFormatter(my_format)
            logger.info("finished storing stock news to database.")
        # Commit the new message as being read
        consumer.commit_offsets()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml",strict_validation=True,validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    logging.info("Main    : before running thread")
    t1.start()
    logging.info("Main    : before joinning thread")
    t1.join()
    logging.info("Main    : all done!")
    app.run(port=8090,debug=True)
