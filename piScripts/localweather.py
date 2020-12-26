import sys
import requests
import logging
import logging.handlers
import os.path
import configparser
import json
import mysql.connector
import datetime


from decimal import Decimal

### global vars ### 
logger = None
db_user = None
db_pw = None
db_host = None
db_schema = None
logfile = None
log_file = None
log_file_size = None
log_file_backup_count = None
open_weather_api_key = None

### config functions ###
def load_config():
    try:
        global db_user
        global db_pw
        global db_host
        global db_schema
        global log_file
        global log_file_size
        global log_file_backup_count
        global open_weather_api_key
        
        if not os.path.isfile("local_weather.ini"):
            raise Exception('Config file is missing!')

        config = configparser.RawConfigParser()
        config.read('local_weather.ini')

        db_user = config.get('MySQL', 'user')
        db_pw = config.get('MySQL', 'password')
        db_host = config.get('MySQL', 'host')
        db_schema = config.get('MySQL', 'schema')

        log_file = config.get('logging', 'logfile')
        log_file_size = config.getint('logging', 'maxBytes')
        log_file_backup_count = config.getint('logging', 'backupCount')

        open_weather_api_key = config.get('openweather','apikey')
    except configparser.Error as err:
        print("Error reading configuration: " + str(err))
        raise

### logging functions ###
def initialize_logging_system():
    global logger
    logger = logging.getLogger('weatherApi')
    logger.setLevel(logging.DEBUG)
    rotatingFileHandler = logging.handlers.RotatingFileHandler(log_file, maxBytes=log_file_size, backupCount=log_file_backup_count)
    formatter = logging.Formatter('%(asctime)s - %(message)s', '%m/%d/%Y %r' )
    rotatingFileHandler.setFormatter(formatter)
	
    logger.addHandler(rotatingFileHandler)

### city id is defined in openweathermap.org city.json index available at 
### http://bulk.openweathermap.org/sample/
### trenton ga id = 4227012
def getLocalTemp(cityId):
    try:
        r = requests.get("http://api.openweathermap.org/data/2.5/weather?id="+str(cityId)+
        "&appid="+open_weather_api_key+"&units=imperial")
        if r.status_code == 200:
            weather = r.json()
            temp = float(weather["main"]["temp"])
            humidity = float(weather["main"]["humidity"])
            description = weather["name"]
            dateRecorded = datetime.datetime.utcfromtimestamp(weather["dt"], )
            return (cityId, temp, humidity, description, dateRecorded)
        else:
            logger.error("Non success from weather api: {} {}".format(str(r.status_code), r.text))
            return 0.0
    finally:
        r.close

### data persistence and manipulation functions ###
def persist_local_weather_to_database(weather):
    # weather is a tuple with the following fields:
    # (cityId, temp, humidity, description, dateRecorded)
    logger.info("Initializing database connection...")
    try:
        cnx = None
        cursor = None
        cnx = mysql.connector.connect(user=db_user, password=db_pw, host=db_host, database=db_schema)
        logger.info("Database connection successful!\n")
        try:
            cursor = cnx.cursor()
            id = weather[0]
            temperature = round(Decimal(weather[1]), 2)
            humidity = round(Decimal(weather[2]), 2)
            description = weather[3]
            dateRecorded = weather[4]
            logger.info("Inserting weather data into database. Values=id:{} description:{} temperature:{} humidity:{} dateRecorded:{}".format(id, description, temperature, humidity, dateRecorded))
            # proc args: locationId VARCHAR(25), description VARCHAR(100),
			#            dateRecorded DATETIME, temperature DECIMAL(5,2), humidity DECIMAL(5,2))
            args =	(id, description, dateRecorded, temperature, humidity)
            cursor.callproc('locationTemperatureInsert', args)	
            result = cursor.fetchone()
            logger.info("Database operations complete! result:{}\n".format(result))	
        except mysql.connector.Error as err:
            logger.error("Error inserting readings into database: "+ str(err))
            raise
        finally:
            if cursor:
                cursor.close()
    except mysql.connector.Error as err:
        logger.error("Unable to connect to database: " + str(err))
        raise
    finally:
        if cnx:
            cnx.close()

def main(cityId):
    load_config()
    initialize_logging_system()
    weather = getLocalTemp(cityId)
    #print(weather[0])
    #print(weather[1])
    #print(weather[2])
    #print(weather[3])
    #print(weather[4])
    if weather:
        persist_local_weather_to_database(weather)


### main execution
if len(sys.argv) != 2:
    raise("Unexpected number of arguments; Please provide city Id")
id = sys.argv[1];
#id = "4227012"
main(id)