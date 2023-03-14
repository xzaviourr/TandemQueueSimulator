import logging
import os
from datetime import datetime


BASE = os.path.dirname(os.path.abspath(__file__))   # Project directory
LOGS_DIR = os.path.join(BASE, "logs")
ITER_LOGS_DIR = os.path.join(LOGS_DIR, f"log_{datetime.now().strftime('%Y%m%d%H%M%S')}")

# Logging
VERBOSE = 1
STREAM_HANDLER_LOGGING_LEVEL = logging.WARNING
FILE_HANDLER_LOGGING_LEVEL = logging.INFO
LOG_FILE_PATHS = {
    "EVENT_HANDLER": os.path.join(ITER_LOGS_DIR, "event_handler.log"),
    "TEMP": os.path.join(ITER_LOGS_DIR, "temp.log")
}

# Setup directories
list_of_directories = [LOGS_DIR, ITER_LOGS_DIR]
for directory in list_of_directories:
    if not os.path.exists(directory):
        os.makedirs(directory)

# Event codes
EVENT_REQUEST_ARRIVAL = 1
EVENT_REQUEST_COMPLETE_FROM_APP_SERVER = 2
EVENT_REQUEST_COMPLETE_FROM_DB_SERVER = 3
EVENT_TIMEOUT = 4

# Request
HIGH_PRIORITY = 1
LOW_PRIORITY = 0
REQUEST_TIMEOUT = 100

# Server
APPLICATION_SERVER = 1
DB_SERVER = 0

SYNCHRONIZE = False