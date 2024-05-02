import time
import paho.mqtt.client as mqtt_client
import hashlib
import random
import logging
import sys
import time
import socket
from logging.handlers import TimedRotatingFileHandler
import requests
import json

server_id = '158.160.151.53:8000'

ip_address = socket.gethostbyname(socket.gethostname())

FORMATTER_STRING = "%(asctime)s — %(name)s — %(levelname)s — %(message)s - IP: {}".format(hashlib.md5(ip_address.encode('utf-8')).hexdigest())

FORMATTER = logging.Formatter(FORMATTER_STRING)
LOG_FILE = "./my_app.log"

INACTIVITY_TIMEOUT = 20

last_message_times = {}

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

logger = get_logger("subscriber_logger")

broker="broker.emqx.io"

def on_message(client, userdata, message):
    time.sleep(1)
    last_message_times[message.topic] = time.time()
    logger.debug("Recieved encoded message.")
    logger.debug("Start message decoding")
    data = str(message.payload.decode("utf-8"))
    logger.debug("Message decoded")
    logger.info(f"received message: {data}")

def check_client_activity():
    curtime = time.time()
    for client, last_message_time in last_message_times.items():
        if curtime - last_message_time >= INACTIVITY_TIMEOUT:
            logger.warning("Publisher isn`t active for a long time.")
            return False
    return True

#client = mqtt_client.Client('isu10012300')
# FOR new version change ABOVE line to
logger.info("Requesting id")
url = 'http://'+server_id+'/get_id'
unique_id=requests.get(url).json()['id']
url = 'http://'+server_id+'/check_id'
valid_id = requests.post(url, json={'id': unique_id}).json()['success']
logger.info(f"Id recieved and validated: {unique_id}")
if valid_id:
    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, unique_id)
    client.on_message=on_message
    logger.info(f"Connecting to broker {broker}")
    client.connect(broker)
    logger.info(f"Connected to broker {broker}") 
    client.loop_start() 
    logger.info("Start subcribing")
    client.subscribe("lab/leds/strip/state")
    while True:
        if check_client_activity():
            time.sleep(10)
            continue
        else:
            break
    logger.info("Stop subscribing")
    logger.info(f"Disconnectind from broker {broker}")
    client.disconnect()
    logger.info(f"Disconnected from broker {broker}")
    client.loop_stop()
