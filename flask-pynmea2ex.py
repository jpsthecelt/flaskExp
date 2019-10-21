import sys
import serial
import pynmea2
import json
from concurrent.futures import threading,lock
import atexit
from flask import Flask,jsonify

from time import gmtime, sleep
from collections import deue

POOL_TIME = 1
class NmeaMsg(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self

    def __getattr__(self, attr):
        return self[attr]

class NmeaStore:
    _currentNmea = NmeaMsg(
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
    def __init__(self):
        self.value = _currentNmea
        self._lock = threading.Lock()

    def lck_putData(self, nMsg):
        with self._lock:
            self.value = nMsg

    def lck_getData(self):
        with self._lock:
            return(self.value)

# Given an NMEA input string, parse and either return it's T/S, alt, lat/lon, etc (as a JSON dict) from the GGA message,
#       or add message-type to the discardQ (returning JSON dict message), or return parse-error message.
def parseGPS(rawMesg):
    # try parsing NMEA message - if it fails, return error
    #                            if it succeeds, look for a message type of 'GGA'
    try:
        msg = pynmea2.parse(rawMesg)
    except pynmea2.ParseError:
        return (NmeaMsg(error_msg=f"Parse-Error: {rawMesg}")

    # if msg-type is not GGA, add the message to the discarded-Q and return appropriate error-message
    # if the msg-type IS GGA, return the timestamp/altitude-lat-lon, etc information
    if msg.sentence_type != 'GGA':
        discardQ.append(msg.sentence_type)
        return (NmeaMsg(error_msg=f"Discarded: {msg.sentence_type}"))
    else:
        return (NmeaMsg(timestamp=msg.timestamp, lat=(msg.lat or 0.0), lat_dir=msg.lat_dir, lon=(msg.lon or 0.0), lon_dir=msg.lon_dir, 
            altitude=(msg.altitude or 0.0), (msg.altitude_units or 'M')))

    def runner():
        try:
            # Initialize discardQ list and and serial-inpuyt channel; clearing out any 'framing errors' in receiving-channel
            #            (we chose to clear out 5 of them)
            QMAX = 100
            discardQ = deue(maxlen=QMAX)
            with serial.Serial("/dev/serial0", 9600, timeout=0.5) as gIn:
                [print("Synchronizing...: {}".format(gIn.readline().decode('ascii', errors='replace'))) for i in range(5)]

                # Then, while it is possible to read messages from the serial-input...
                #       parse the data, if valid then update the 'data-store', and output a descriptive message
                while True:
                    nMsg = parseGPS(gIn.readline().decode('ascii', errors='replace')))
                    lck_putData(nMsg)
                    print(json.dumps(nMsg))
                    time.sleep(1)

        except (KeyboardInterrupt,SystemExit):
            print("...Terminated!")
            print("Last {len(discardQ)} discarded messages were {discardQ}")
            sys.exit()

@app.route('/')
def mainGPS():
    return jsonify(lck_getData())

def create_app():
    flask_app= Flask(__name__)

    def interrupt():
        global gpsUpdater
        gpsUpdater.cancel()

    def doStuff():
        global commonDataStruct
        global gpsUpdater
        with dataLock:
        # Do your stuff with commonDataStruct Here

        # Set the next thread to happen
        gpsUpdater = threading.Timer(POOL_TIME, doStuff, ())
        gpsUpdater.start()

    def doStuffStart():
        # Do initialisation stuff here
        global gpsUpdater
        # Create your thread
        gpsUpdater = threading.Timer(POOL_TIME, runner, ())
        gpsUpdater.start()

    # Initiate
    doStuffStart()
    # When you kill Flask (SIGTERM), clear the trigger for the next thread
    atexit.register(interrupt)
    return app

app = create_app()

