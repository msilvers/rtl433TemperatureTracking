#!/usr/bin/python3

import sys
import logging
import logging.handlers
import os.path
import subprocess
import json
import mysql.connector
import configparser

import time

from decimal import Decimal


### global vars ### 
logger = None
runtime_seconds = 90
db_user = None
db_pw = None
db_host = None
db_schema = None
logfile = None

def main():
	load_config()
	initialize_logging_system()
	logger.info("***** Process start *****")
	rawData = get_sensor_data()
	sensorReadings = coalesce_list_to_dictionary(rawData)
	persist_sensor_readings_to_database(sensorReadings)
	logger.info("***** Process complete *****")

	#for row in sensorReadings.values():
	#	print "id: "+str(row["id"]) + " temp: " + str(row["temperature_C"]) + " recorded at utc: " + str(row["time"])



### config functions ###
def load_config():
	try:
		global db_user
		global db_pw
		global db_host
		global db_schema
		global runtime_seconds
		global log_file
		global log_file_size
		global log_file_backup_count


		if not os.path.isfile("process_rtl_433.ini"):
			raise Exception('Config file is missing!')

		config = configparser.RawConfigParser()
		config.read('process_rtl_433.ini')

		db_user = config.get('MySQL', 'user')
		db_pw = config.get('MySQL', 'password')
		db_host = config.get('MySQL', 'host')
		db_schema = config.get('MySQL', 'schema')

		runtime_seconds = config.get('rtl433', 'runSeconds')

		log_file = config.get('logging', 'logfile')
		log_file_size = config.getint('logging', 'maxBytes')
		log_file_backup_count = config.getint('logging', 'backupCount')

	except configparser.Error as err:
		print("Error reading configuration: " + str(err))
		raise

### logging functions ###
def initialize_logging_system():
	global logger

	logger = logging.getLogger('rtl')
	logger.setLevel(logging.DEBUG)
	rotatingFileHandler = logging.handlers.RotatingFileHandler(log_file, maxBytes=log_file_size, backupCount=log_file_backup_count)
	formatter = logging.Formatter('%(asctime)s - %(message)s', '%m/%d/%Y %r' )
	rotatingFileHandler.setFormatter(formatter)

	logger.addHandler(rotatingFileHandler)



### subprocess managment functions ###
def get_sensor_data():
	# returns sensor data as a list of strings
	logger.info("Launching subprocess to read sensor data...")

	sensorProcess = subprocess.Popen("rtl_433 -M time:utc -q -R 40 -F json -T {}".format(runtime_seconds), stdout=subprocess.PIPE, shell=True)
	returnCode = sensorProcess.wait()
	data = sensorProcess.stdout.readlines()
	logger.info("Completed reading sensor data with return code: "+str(returnCode) + " Received {} sensor readings\n".format(len(data)))
	return data


### utility functions ### 
def get_hash_key(jsonSensorData):
	key = str(jsonSensorData["id"]) + str(jsonSensorData["time"])
	return key

def string_to_json(jsonString):
	return json.loads(jsonString)

def coalesce_list_to_dictionary(dataItems):
	logger.info("Parsing raw sensor data and removing duplicates...") 
	uniqueRows = {}
	for item in dataItems:
		key = get_hash_key(string_to_json(item))
		if key not in uniqueRows:
			uniqueRows[key] = string_to_json(item)
	logger.info("Completed parsing raw sensor data. Identified {} unique readings\n".format(len(uniqueRows)))
	return uniqueRows
	
### data persistence and manipulation functions ###
def persist_sensor_readings_to_database(sensorReadings):
	logger.info("Initializing database connection...")
	try:
		cnx = None
		cursor = None
		cnx = mysql.connector.connect(user=db_user, password=db_pw, host=db_host, database=db_schema)
		logger.info("Database connection successful!\n")
		try:
			cursor = cnx.cursor()
			logger.info("Inserting {} rows into database...".format(len(sensorReadings)))
			for reading in sensorReadings.values():
			        #proc args: sensorId VARCHAR(25), dateRecorded DATETIME, batteryLow TINYINT(1),  temperatureCelsius DECIMAL(5,2), humidity DECIMAL(5,2)
				temperature = round(Decimal(reading["temperature_C"]), 2)
				humidity = round(Decimal(reading["humidity"]), 2)
				batteryOk = reading["battery_ok"]
				batteryLow = not(batteryOk)
				args =	(str(reading["id"]), reading["time"], int(batteryLow),  temperature, humidity)
				cursor.callproc('sensorReadingInsert', args)	
			logger.info("Database operations complete!\n")	
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

### main execution
main()