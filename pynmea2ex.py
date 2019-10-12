import sys
import serial
import pynmea2
import json

def parseGPS(rawMesg):
    try:
        msg = pynmea2.parse(rawMesg)
    except pynmea2.ParseError:
        return str("{{Error: {}}}".format(rawMesg))

    if msg.sentence_type != 'GGA':
        return str("{{Message discarded: {}}}".format(msg.sentence_type))
    else:
        return str("{{Timestamp: {}, Lat: {} {} ,  Lon: {} {}, Altitude: {} {}}}".format(
                  msg.timestamp,msg.lat or 0.0,msg.lat_dir,msg.lon or 0.0,msg.lon_dir,msg.altitude or 0.0,msg.altitude_units or 'M'))

try:
    with serial.Serial("/dev/serial0", 9600, timeout=0.5) as gIn:
        [print("Synchronizing...: {}".format(gIn.readline().decode('ascii', errors='replace'))) for i in range(5)]
            
        while True:
            print(parseGPS(gIn.readline().decode('ascii', errors='replace')))

except (KeyboardInterrupt,SystemExit):
    print("...Terminated!")
    sys.exit()
