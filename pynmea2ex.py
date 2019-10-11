import sys
import serial
import pynmea2
import json

def parseGPS(rawMesg):
    try:
        msg = pynmea2.parse(rawMesg)
    except pynmea2.ParseError:
        return str("{{Parse Error: {}}}".format(rawMesg))

    if msg.sentence_type != 'GGA':
        return str("{{Message discarded: {}}}".format(msg.sentence_type))
    else:
        return str("{{Timestamp: {}, Lat: {} {} ,  Lon: {} {}, Altitude: {} {}}}".format(
                  msg.timestamp,msg.lat,msg.lat_dir,msg.lon,msg.lon_dir,msg.altitude,msg.altitude_units))

try:
    with serial.Serial("/dev/serial0", 9600, timeout=0.5) as gIn:
        print("Initial data synchronization: %s", [gIn.readline().decode('ascii', errors='replace') for i in range(5)])
            
        while True:
            print("parsed output message is: ", parseGPS(gIn.readline().decode('ascii', errors='replace')))

except (KeyboardInterrupt,SystemExit):
    print("...Terminated!")
    sys.exit()
