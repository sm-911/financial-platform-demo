import logging
import json
from pythonjsonlogger import jsonlogger

def get_logger(name: str = "app"):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        logHandler = logging.StreamHandler()
        formatter = jsonlogger.JsonFormatter('%(asctime)s %(name)s %(levelname)s %(message)s')
        logHandler.setFormatter(formatter)
        logger.addHandler(logHandler)
    return logger
