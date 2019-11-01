import sys
import serial
import pynmea2
import json
import time
from __future__ import division
from datetime import datetime, timedelta
from collections import deque
import argparse
from time import sleep
from collections import deque

import atexit
import threading
from flask import Flask,jsonify
import copy
import logging

GPS_CYCLE_TIME = 1

# Also overriding deepcopy to add to class-methods
class nmea_msg(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self
    def __getattr__(self, attr):
        return self[attr]
    def __deepcopy__(self, memo):
        return nmea_msg(copy.deepcopy(dict(self)))

_current_nmea_msg = nmea_msg(
     timestamp = datetime.now().timestamp(),
     lat =       0.0,
     lat_dir =   '0',
     lon =       0.0,
     lon_dir =   '0',
     altitude =  0.0,
     altitude_units = 'M',
     got_fix =   False,
     num_sats =  0,
     error_msg = ''
     )

def totimestamp(dt, epoch=datetime(1970,1,1)):
        td = dt - epoch
            # return td.total_seconds()
                return (td.microseconds + (td.seconds + td.days * 86400) * 10**6) / 10**6

# Given an NMEA input string (from attached GPS device), parse and either return it's T/S, 
#       alt, lat/lon, etc (as a JSON dict) from the GGA message, add message-type to the 
#       discardQ (based on command-line 'verbose' switch), finally returning JSON dict message), 
#       or else return parse-error message.
def parseGPS(raw_mesg, discardIt):
    # try parsing NMEA message - if it fails, return error
    #                            if it succeeds, look for a message type of 'GGA'
    try:
        msg = pynmea2.parse(raw_mesg)
    except pynmea2.ParseError:
        logging.info('parsedGPS: Failed to parse NMEA message...')
        return ( nmea_msg(timestamp = datetime.now().timestamp(), lat=0.0, lat_dir='0', lon=0.0, lon_dir='0', altitude=0.0, altitude_units='M',
             got_fix=False, num_sats=0, error_msg="Parse-Error: %s" % raw_mesg))

    # if msg-type is not GGA, add the message to the discarded-Q and return appropriate error-message
    # if the msg-type IS GGA, return the timestamp/altitude-lat-lon, etc information
#    print(f"The data fields are: \n")
#    ['%s: %s' % (msg.fields[i][0], msg.data[i]) 
#                 for i in range(len(msg.fields))]
    if msg.sentence_type != 'GGA':
        discardQ.append(msg.sentence_type)
        if discardIt:
            em=f"Discarded: {msg.sentence_type}, t/s: {totimestamp(msg.timestamp)}"
        else:
            em=f"Not-Discarded: {msg.sentence_type}, t/s: {totimestamp(msg.timestamp)}"
        logging.info('parseGPS: returning discarded NMEA message...%s' % em)
#        return ( nmea_msg(timestamp = datetime.now().timestamp(), lat=0.0, lat_dir='0', lon=0.0, lon_dir='0', altitude=0.0, altitude_units='M', got_fix=False,
#           num_sats=0, error_msg=em))
        return msg

    else:
        # (recall that gps_qual == 0 is 'no fix', or fix=False, 1 == fix, 2-5 are fix-other)
        logging.info('\nparseGPS: Newly parsed NMEA message before return')
        with db_lock:
            _current_nmea_msg = copy.deepcopy(nmea_msg(timestamp=msg.timestamp, lat=(msg.lat or 0.0), lat_dir=msg.lat_dir, lon=(msg.lon or 0.0), lon_dir=msg.lon_dir, 
               altitude=(msg.altitude or 0.0), altitude_units=(msg.altitude_units or 'M'), got_fix=(msg.gps_qual==1), num_sats=0, error_msg=''))
        return msg

def update_gps():
#    try:
        logging.info('attempting attach serial-device & obtain messages...')
        with serial.Serial(results.gps_device_string, 9600, timeout=0.5) as gIn:
            [print("Synchronizing...: {}".format(gIn.readline().decode('ascii', errors='replace'))) for i in range(5)]
                
            # Then, while it is possible to read messages from the serial-input, read & parse input data
            #       printing out result
            while True:
                time.sleep(1)
                nmea_rxd_msg = parseGPS(gIn.readline().decode('ascii', errors='replace'), results.v)
#                    del nmea_rxd_msg
                print("\njson.dumps() of updated _current_nmea_msg looks like:",json.dumps(_current_nmea_msg))
    
    # process any system-exit errors or ^c received, outputting our discardQ contents 'before we go'
#    except (KeyboardInterrupt,SystemExit):
#        gps_update_thread.cancel()
#        print("...Terminated!")
#        print(f"Last {len(discardQ)} discarded messages were {discardQ}\n\n")
#        sys.exit()

def interrupt():
    logging.info('got interrupt)...')
    gps_update_thread.cancel()
    exit()

if __name__ == '__main__':
    # Initialize discardQ list and and serial-input channel; clearing out any 'framing errors' in receiving-channel 
    #            (we chose to clear out 5 of them)
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    logging.getLogger().setLevel(logging.INFO)

    QMAX = 100
    discardQ = deque(maxlen=QMAX)
    parser = argparse.ArgumentParser(description='Grab and display incoming GPS messages via flask website')
    parser.add_argument('-v', default=False, action='store_true', help='print all discarded messages ')
    parser.add_argument('gps_device_string', action='store', default='/dev/serial0', help='device from which we will connect for GPS messages')
    results = parser.parse_args()
    
    print("\nInitial current NMEA message looks like:",json.dumps(_current_nmea_msg))
    db_lock = threading.Lock()
    gps_update_thread = threading.Timer(GPS_CYCLE_TIME, update_gps, ())
    atexit.register(interrupt)
    gps_update_thread.start()

    try:
        while True:
            sleep(5)
            logging.info('main (after 5 sec sleep)...')

            with db_lock:
                print("\nin main; dumping _current_nmea_msg)",json.dumps(_current_nmea_msg))
    except (KeyboardInterrupt,SystemExit):
        gps_update_thread.cancel()
        print("...Terminated!")
        print(f"Last {len(discardQ)} discarded messages were {discardQ}\n\n")


#@app.route('/')
#def mainGPS():
#    return jsonify(lck_getData())

#def create_app():
#    flask_app= Flask(__name__)

#def interrupt():
#    global gps_update_thread
#    gps_update_thread.cancel()

#def doStuff():
#    #global commonDataStruct
#    global gps_update_thread
#    # with dataLock:
#    # Do your stuff with commonDataStruct Here
#
#    # Set the next thread to happen
#    gps_update_thread = threading.Timer(GPS_CYCLE_TIME, doStuff, ())
#    gps_update_thread.start()

#def gps_thread_start():
#    # Initialize threading,here
#    global gps_update_thread
#    # Create your thread
#    gps_update_thread = threading.Timer(GPS_CYCLE_TIME, gps_update, ())
#    gps_update_thread.start()

    # Initiate
#    gps_thread_start()
    # When you kill Flask (SIGTERM), clear the trigger for the next thread
#    atexit.register(interrupt)
#    return app
#    gps_update_thread.join()

#    create_app()
#    app = create_app()

