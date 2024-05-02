import time
import requests
import paho.mqtt.client as mqtt_client
import hashlib
import json
import random
import logging
import sys
import socket
from logging.handlers import TimedRotatingFileHandler

server_id = '158.160.151.53:8000'

ip_address = socket.gethostbyname(socket.gethostname())

FORMATTER_STRING = "%(asctime)s — %(name)s — %(levelname)s — %(message)s - IP: {}".format(hashlib.md5(ip_address.encode('utf-8')).hexdigest())

FORMATTER = logging.Formatter(FORMATTER_STRING)
LOG_FILE = "./my_app.log"


def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    logger.addHandler(console_handler)

    file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight')
    file_handler.setFormatter(FORMATTER)
    logger.addHandler(file_handler)

    return logger

logger = get_logger("publish_logger")

broker="broker.emqx.io"

#client = mqtt_client.Client('isu10012300')
# FOR new version change ABOVE line to 
logger.info("Requesting id")
url = 'http://'+server_id+'/get_id'
unique_id=requests.get(url).json()['id']
url = 'http://'+server_id+'/check_id'
valid_id = requests.post(url, json={'id': unique_id}).json()['success']
logger.info(f"Id received and validated: {unique_id}")
if valid_id:
    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, unique_id)
    logger.info(f"Connecting to broker {broker}")
    client.connect(broker)
    logger.info(f"Connected to broker {broker}")
    client.loop_start() 
    logger.info(f"Start publishing")
    for i in range(10):
        state = "demid"
        state = state[i:] + state[:i]
        logger.info(f"publishing {state}")
        client.publish("lab/leds/strip/state", state)
        time.sleep(2)
    logger.info(f"Stop publishing")
    logger.info(f"Disconnecting from broker {broker}")
    client.disconnect()
    logger.info(f"Disconnected from broker {broker}")
    client.loop_stop()
