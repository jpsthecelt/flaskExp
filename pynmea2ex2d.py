import sys
import serial
import pynmea2
import json
import time
from datetime import datetime
from collections import deque
import argparse
from time import sleep
from collections import deque

import atexit
import threading
from flask import Flask,jsonify
import logging

GPS_CYCLE_TIME = 1

class nmea_msg(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self
    def __getattr__(self, attr):
        return self[attr]

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
    if msg.sentence_type != 'GGA':
        fix = msg.gps_qual == 1
        discardQ.append(msg.sentence_type)
        if discardIt:
           em="Discarded: %s" % msg.sentence_type
        else:
           em="Not-Discarded: %s" % msg.sentence_type
        logging.info('parseGPS: returning discarded NMEA message...')
        return ( nmea_msg(timestamp = msg.timestamp, lat=0.0, lat_dir='0', lon=0.0, lon_dir='0', altitude=0.0, altitude_units='M', got_fix=fix,
           num_sats=0, error_msg=em))

    else:
        # (recall that gps_qual == 0 is 'no fix', or fix=False, 1 == fix, 2-5 are fix-other)
        logging.info('\nparseGPS: Newly parsed NMEA message before return')
        return (nmea_msg(timestamp=msg.timestamp, lat=(msg.lat or 0.0), lat_dir=msg.lat_dir, lon=(msg.lon or 0.0), lon_dir=msg.lon_dir, 
           altitude=(msg.altitude or 0.0), altitude_units=(msg.altitude_units or 'M'), got_fix=(msg.gps_qual==1), num_sats=0, error_msg=''))

def update_gps():
    try:
        logging.info('attempting attach serial-device & obtain messages...')
        with serial.Serial(results.gps_device_string, 9600, timeout=0.5) as gIn:
            [print("Synchronizing...: {}".format(gIn.readline().decode('ascii', errors='replace'))) for i in range(5)]
                
            # Then, while it is possible to read messages from the serial-input, read & parse input data
            #       printing out result
            while True:
                nmea_rxd_msg = parseGPS(gIn.readline().decode('ascii', errors='replace'), results.v)
                logging.info('update_gps: parsed new nmea-message; updating _current...')
                print("\nupdate_gps: Newly parsed NMEA message looks like:",json.dumps(nmea_rxd_msg))
                with db_lock:
                    _current_nmea_msg = nmea_rxd_msg
                    del nmea_rxd_msg
                print("\nUpdated current NMEA message looks like:",json.dumps(_current_nmea_msg))
                time.sleep(1)
    
    # process any system-exit errors or ^c received, outputting our discardQ contents 'before we go'
    except (KeyboardInterrupt,SystemExit):
        gps_update_thread.cancel()
        print("...Terminated!")
        print(f"Last {len(discardQ)} discarded messages were {discardQ}\n\n")
        sys.exit()

def interrupt():
    logging.info('got interrupt)...')
    gps_update_thread.cancel()

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

    logging.info('main starting wait')
    while True:
        sleep(5)
        logging.info('main (after sleep)...')

        with db_lock:
            print("\nin main; dumping _current_nmea_msg)",json.dumps(_current_nmea_msg))
