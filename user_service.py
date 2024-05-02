from fastapi import FastAPI, Request
import hashlib
import datetime
from pydantic import BaseModel
import logging
import sys
import socket
from logging.handlers import TimedRotatingFileHandler

class Id(BaseModel):
	id: str

ids = {}

ip_address = socket.gethostbyname(socket.gethostname())

FORMATTER_STRING = "%(asctime)s — %(name)s — %(levelname)s — %(message)s - IP: {}".format(hashlib.md5(ip_address.encode('utf-8')).hexdigest())
FORMATTER = logging.Formatter(FORMATTER_STRING)
LOG_FILE = "./my_app.log" # use fancy libs to make proper temp file

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

logger = get_logger("User_service_logger")

logger.info("Launching FastAPI server")
app = FastAPI()
logger.info("FastAPI server is working")

@app.get('/get_id')
def get_id(request: Request):
    client_host= request.client.host
    ip_hash = hashlib.md5(client_host.encode('utf-8')).hexdigest()
    logger.debug("Getted request for unique id")
    logger.debug("Generating unique id")
    time_str = str(datetime.datetime.now())
    id = hashlib.md5(time_str.encode('utf-8')).hexdigest()
    logger.info(f"Unique id for user {ip_hash} generated: {id}")
    ids[id]=ip_hash
    print(ids)
    return {"id": id}

@app.post('/check_id')
def check_id(item: Id, request : Request):
	client_host= request.client.host
	ip_hash = hashlib.md5(client_host.encode('utf-8')).hexdigest()
	id = item.id
	print(id)
	print(ip_hash)
	if id in ids:
		if ids[id]==ip_hash:
			return {"success": True}
		else:
			message = "This id is already in use."
			logger.error("2 users with same id")
			return {"success": False, "message" : message}
	else:
		message = "Unknown id"
		logger.error("Unknown id")
		return {"success": False, "message": message}
