import sys
import serial
import pynmea2
import json
import threading
import atexit
import argparse
#from flask import Flask,jsonify

from time import gmtime, sleep
from collections import deque

GPS_CYCLE_TIME = 1
class nmea_msg(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self

    def __getattr__(self, attr):
        return self[attr]

nmea_dblock = threading.Lock()

nmea_current = nmea_msg(
     timestamp = gmtime(),
     lat =       0.0,
     lat_dir =   '0',
     lon =       0.0,
     lon_dir =   '0',
     altitude =  0.0,
     alt_units = 'M',
     got_fix =   False,
     num_sats =  0,
     error_msg = ''
     )

def lck_putdata(nmsg):
    with nmea_dblock:
        nmea_current = nmsg

def lck_getdata():
    with nmea_dblock:
        return(nmea_current)

# Given an NMEA input string, parse and either return it's T/S, alt, lat/lon, etc (as a JSON dict) from the GGA message,
#       or add message-type to the discardQ (returning JSON dict message), or return parse-error message.
# try parsing NMEA message - if it fails, return error
#                            if it succeeds, look for a message type of 'GGA'
    # if msg-type is not GGA, add the message to the discarded-Q and return appropriate error-message
    # if the msg-type IS GGA, return the timestamp/altitude-lat-lon, etc information
def parseGPS(raw_mesg):
    try:
        msg = pynmea2.parse(raw_msg)
    except pynmea2.ParseError:
        return (nmea_msg(error_msg=f"Parse-Error: {raw_msg}")

    if (msg.sentence_type != 'GGA'):
        discardQ.append(msg.sentence_type)
        return (nmea_msg(error_msg=f"Discarded: {msg.sentence_type}"))
    else:
        return (nmea_msg(timestamp=msg.timestamp, lat=(msg.lat or 0.0), lat_dir=msg.lat_dir, lon=(msg.lon or 0.0), lon_dir=msg.lon_dir, 
            altitude=(msg.altitude or 0.0), (msg.altitude_units or 'M')))

def gps_update():
    try:
        # Initialize discardQ list and and serial-inpuyt channel; clearing out any 'framing errors' in receiving-channel
        #            (we chose to clear out 5 of them)
        QMAX = 100
        discardQ = deque(maxlen=QMAX)
        with serial.Serial(results.device, 9600, timeout=0.5) as gIn:
            [print("Synchronizing...: {}".format(gIn.readline().decode('ascii', errors='replace'))) for i in range(5)]

            # Then, while it is possible to read messages from the serial-input...
            #       parse the data, if valid then update the 'data-store', and output a descriptive message
            while True:
                nMsg = parseGPS(gIn.readline().decode('ascii', errors='replace')))
                lck_putdata(nMsg)
                print(json.dumps(nMsg))
                time.sleep(1)

    except (KeyboardInterrupt,SystemExit):
        print("...Terminated!")
        print("Last {len(discardQ)} discarded messages were {discardQ}")
        sys.exit()

#@app.route('/')
#def mainGPS():
#    return jsonify(lck_getData())

#def create_app():
#    flask_app= Flask(__name__)

def interrupt():
#    global gps_update_thread
    gps_update_thread.cancel()

#def doStuff():
#    #global commonDataStruct
#    global gps_update_thread
#    # with dataLock:
#    # Do your stuff with commonDataStruct Here
#
#    # Set the next thread to happen
#    gps_update_thread = threading.Timer(GPS_CYCLE_TIME, doStuff, ())
#    gps_update_thread.start()

def gps_thread_start():
    # Initialize threading,here
#    global gps_update_thread
    # Create your thread
    gps_update_thread = threading.Timer(GPS_CYCLE_TIME, gps_update, ())
    gps_update_thread.start()

if __name__ = '__main__':
    parser = argparse.ArgumentParser(description='Grab and display incoming GPS messages via flask website')
    parser.add_argument('-v', default=False, action='store_false', help='print all discarded messages ')
    parser.add_argument('--device', default='/dev/serial0', action='store', help='name of serial device to poll for GPS data')
    results = parser.parse_args()

    # Initiate
    gps_thread_start()
    # When you kill Flask (SIGTERM), clear the trigger for the next thread
    atexit.register(interrupt)
#    return app
    gps_update_thread.join()

#    create_app()
#    app = create_app()

