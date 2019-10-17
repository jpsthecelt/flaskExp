import sys
import serial
import pynmea2
import json

from flask import flask,jsonify

import time
from collections import deque

# Given an NMEA input string, parse and either return it's T/S, alt, lat/lon, etc (as a JSON dict) from the GGA message,
#       or add message-type to the discardQ (returning JSON dict message), or return parse-error message.
def parseGPS(rawMesg):
    # try parsing NMEA message - if it fails, return error
    #                            if it succeeds, look for a message type of 'GGA'
    try:
        msg = pynmea2.parse(rawMesg)
    except pynmea2.ParseError:
        return (f"{{Parse-Error: {rawMesg}}}")

    # if msg-type is not GGA, add the message to the discarded-Q and return appropriate error-message
    # if the msg-type IS GGA, return the timestamp/altitude-lat-lon, etc information
    if msg.sentence_type != 'GGA':
        discardQ.append(msg.sentence_type)
        return (f"{{Discarded: {msg.sentence_type}}}")
    else:
        return (f"{{Timestamp: {msg.timestamp}, Lat: {msg.lat or 0.0} {msg.lat_dir},  Lon: {msg.lon or 0.0} {msg.lon_dir}, Altitude: {msg.altitude or 0.0} {msg.altitude_units or 'M'}}}")

flask_app= flask(__name__)
app = create_app()

@app.route('/')
def mainGPS():
    runner()

def runner():
    try:
        # Initialize discardQ list and and serial-inpuyt channel; clearing out any 'framing errors' in receiving-channel 
        #            (we chose to clear out 5 of them)
        QMAX = 100
        discardQ = deque(maxlen=QMAX)
        with serial.Serial("/dev/serial0", 9600, timeout=0.5) as gIn:
            [print("Synchronizing...: {}".format(gIn.readline().decode('ascii', errors='replace'))) for i in range(5)]
                
            # Then, while it is possible to read messages from the serial-input
            while True:
                print(parseGPS(gIn.readline().decode('ascii', errors='replace')))
                time.sleep(1)

    except (KeyboardInterrupt,SystemExit):
        print("...Terminated!")
        print("Last {len(discardQ)} discarded messages were {discardQ}")
        sys.exit()

