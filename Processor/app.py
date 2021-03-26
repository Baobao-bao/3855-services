import connexion 
from connexion import NoContent
from swagger_ui_bundle import swagger_ui_path

import datetime
import logging
import logging.config
import yaml
from apscheduler.schedulers.background import BackgroundScheduler
import json
from datetime import date
import requests
from datetime import datetime


with open("app_conf.yml", "r") as f:
    app_config = yaml.safe_load(f.read())

with open("log_conf.yml", "r") as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)



logger = logging.getLogger('basicLogger')
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)


def get_stats():
    with open('data.json' ,"r") as file:
        data=json.load(file)
    return data[0], 200

def populate_stats():
    """ Periodically update stats """
    today = date.today()
    today = str(today)

    now = datetime.now()
    now = now.strftime("%d-%b-%Y (%H:%M:%S.%f)")
    default=[{
        "num_sp_readings":100,
        "num_sn_readings":100,
        "max_sp_reading":100,
        "min_sp_reading":100,
        "last_updated": now
    }]
    logger.info("Start Periodic Processing")
    # If the file doesn’t yet exist, use default values for the stats
    try:
        with open('data.json' ,"r") as file:
            # content = file.read()
            # data = json.loads(content)
            data=json.load(file)
    except:
        data=default

    price_res = requests.get(app_config["eventstore"]["url"]+"/open-price?timestamp="+today)
    news_res = requests.get(app_config["eventstore"]["url"]+"/news?timestamp="+today)
    # print(price_res.text)
    # print(news_res.text)

    price_list = price_res.json()
    news_list = news_res.json()
    seq = [x['open_price'] for x in price_list] #string indices must be integers
    lowest_price = min(seq)
    highest_price = max(seq)

    stat_info ={
            "num_sp_readings":len(list(price_res.text)),
            "num_sn_readings":len(list(news_res.text)),
            "max_sp_reading":highest_price,
            "min_sp_reading":lowest_price,
            "last_updated":now
        }

    if (price_res.status_code == 200 and news_res.status_code == 200 ):
        logger.info(stat_info)
        data.insert(0,stat_info)
        with open('data.json' ,"w") as file:
            json.dump(data, file)
    else:
        logger.error("fail to get data from storage service.")
    


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,'interval',seconds=app_config['scheduler']['period_sec'])
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml",strict_validation=True,validate_responses=True)

if __name__ == "__main__":
     # run our standalone gevent server
    init_scheduler()
    app.run(port=8100,debug=True,use_reloader=False)
