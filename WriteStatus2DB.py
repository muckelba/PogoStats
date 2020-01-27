#!/usr/bin/env python3
__author__ = "GhostTalker"
__copyright__ = "Copyright 2019, The GhostTalker project"
__version__ = "0.3.0"
__status__ = "Dev"

# generic/built-in and other libs
import os
import sys
import time
import datetime
import pymysql.cursors
import pymysql

#########################################################################################################
#########################################################################################################
#
# Configuration
# 
statusOfflineTimeout = 10            # in minutes, Device is offline when ProtoDate older then this value
statusInterval = 30                  # in seconds, Fetching intervall for status
cleanupDbEntryOlderThan = 14         # in days, Deleting entries from destdb older than configured days
#
# DB configuration
#
def connect_sourcedb(): 
    connectionSourceDB = pymysql.connect(host=os.environ['SCANNER_HOST'],
                             user=os.environ['SCANNER_USER'],
                             password=os.environ['SCANNER_PASSWORD'],
                             db=os.environ['SCANNER_DATABASE'],
                             cursorclass=pymysql.cursors.DictCursor)
    return connectionSourceDB
#
def connect_destdb(): 							 
    connectionDestDB = pymysql.connect(host='database',
                             user=os.environ['GRAFANA_USER'],
                             password=os.environ['GRAFANA_PASSWORD'],
                             db=os.environ['GRAFANA_DATABASE'],
                             cursorclass=pymysql.cursors.DictCursor)
    return connectionDestDB						 
#########################################################################################################
#########################################################################################################

def check_status_table_from_sourcedb():
    try:
        connectionSourceDB = connect_sourcedb()
        with connectionSourceDB.cursor() as cursor:
            # Read a single record
            sql = "SELECT `settings_device`.`name` AS `origin`, `trs_status`.`lastProtoDateTime`, `trs_status`.`currentSleepTime` FROM `trs_status` LEFT JOIN `settings_device` ON `trs_status`.`device_id` = `settings_device`.`device_id`"
            cursor.execute(sql)
            SourceStatusDict = cursor.fetchall()
            #print("Source:")
            #print("---------------------------------------------")        
            #print(SourceStatusDict)
            #print("---------------------------------------------")
    finally:
        connectionSourceDB.close()
        return SourceStatusDict

def calc_past_min_from_now(timedate):
    """ calculate time between now and given timedate """
    actual_time = time.time()
    if timedate == None or timedate == "":
        return 99999
    timedate = datetime.datetime.strptime(str(timedate), '%Y-%m-%d %H:%M:%S').timestamp()
    past_sec_from_now = actual_time - timedate
    past_min_from_now = past_sec_from_now / 60
    past_min_from_now = int(past_min_from_now)
    return past_min_from_now

def check_online_offline_status(lastProtoDateTime):
    if calc_past_min_from_now(lastProtoDateTime) < statusOfflineTimeout:
        return 1
    else:
        return 0

### Dirty fix: wait a bit until the DB is reachable:

time.sleep(10)

try:
    while 1:
        now = datetime.datetime.now() # current date and time
        print(now.strftime("%m/%d/%Y, %H:%M:%S"))
        # Create new records
        try:
            connectionDestDB = connect_destdb()
            i = 0
            with connectionDestDB.cursor() as cursor:
                for entry in check_status_table_from_sourcedb():
                    save_data = "INSERT INTO `status`(`createdate`, `origin`, `status`, `time`) VALUES('{}','{}','{}','{}')".format(datetime.date.today(), entry["origin"], check_online_offline_status(entry["lastProtoDateTime"]), entry["lastProtoDateTime"])
                    cursor.execute(save_data)
                    # connection is not autocommit by default. So you must commit to save your changes.
                    connectionDestDB.commit()
                    i = i + 1
        finally:
            print("new records done")
        
    	# delete old entrys
        try:
            with connectionDestDB.cursor() as cursor:
                del_data = "DELETE FROM `status` where `createdate` < CURDATE() - INTERVAL {} DAY;".format(cleanupDbEntryOlderThan)
                cursor.execute(del_data)
                # connection is not autocommit by default. So you must commit to save your changes.
                connectionDestDB.commit()
        finally:
            print("cleanup done")
            connectionDestDB.close()    
        time.sleep(statusInterval)
	
except KeyboardInterrupt:
    pass
    print('QUIT')