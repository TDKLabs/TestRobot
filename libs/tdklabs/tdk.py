import os
HOST = os.getenv('JBOSSHOST',None)
PORT = os.getenv('JBOSSPORT',None)
ORACLE = os.getenv('ORACLE',None)
HADOOP_ENV= None
DB_USER = None
DB_PASSWORD = None
DB_SID = None
DB_SERVICE = None
DB_CONNECTOR = None
DB_PORT = None
BROWSER = 'Firefox'
MQ_ENV = None

ENV = None
LOG_HOST = None
LOG_PATH = None
LOG_USERNAME = None
LOG_PASSWD = None

SCREENSHOT_DIR = os.getenv('SCREENSHOT_DIR','screenshots')
