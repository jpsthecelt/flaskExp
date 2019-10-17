import sys
import serial
import pynmea2
import json
from flask import Flask,jsonify
import pdb
import time

def parseGPS(rawMesg):
    try:
        msg = pynmea2.parse(rawMesg)
    except pynmea2.ParseError:
        return str("{{Error: {}}}".format(rawMesg))

    if msg.sentence_type != 'GGA':
        return str("{{Discarded: {}}}".format(msg.sentence_type))
    else:
        print(jsonify(timestamp=msg.timestamp,lat=msg.lat,latDir=msg.lat_dir,
            lon=msg.lon,LonDir=msg.lon_dir,
            altitude=msg.altitude,units=msg.altitude_units))
        return str("{{Timestamp: {}, Lat: {} {} ,  Lon: {} {}, Altitude: {} {}}}".format(
                  msg.timestamp,msg.lat or 0.0,msg.lat_dir,msg.lon or 0.0,msg.lon_dir,msg.altitude or 0.0,msg.altitude_units or 'M'))

@app.route('/')
def mainGPS():
    runner()

def runner():
    try:
        pdb.set_trace()
        with serial.Serial("/dev/serial0", 9600, timeout=0.5) as gIn:
            [print("Synchronizing...: {}".format(gIn.readline().decode('ascii', errors='replace'))) for i in range(5)]
                
            while True:
                print(parseGPS(gIn.readline().decode('ascii', errors='replace')))
                time.sleep(1)
    
    except (KeyboardInterrupt,SystemExit):
        print("...Terminated!")
        sys.exit()
