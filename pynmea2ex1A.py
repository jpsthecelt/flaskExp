import sys
import serial
import pynmea2
import json
import jsonify

def parseGPS(rawMesg):
    try:
        msg = pynmea2.parse(rawMesg)
    except pynmea2.ParseError:
        return(f"{{Parse Error {pynmea2.exception}}}"

    if msg.sentence_type != 'GGA'):
            return (f"{{Discarded: {msg.sentence_type}}}")
    else:
        return (f"{{Timestamp: {msg.timestamp} -- Lat: {msg.lat} {msg.lat_dir} -- Lon: {msg.lon} {msg_lon_dir} -- Altitude: {msg.altitude} {msg.altitude_units}}}")

try:
    with serial.Serial("/dev/serial0", 9600, timeout=0.5) as gIn:
        for i in range(5):
            data = gIn.readline().decode('ascii', errors='replace')
            print(f"Initial data synchronization: {data}")
            
        while True:
            for msg in gIn.next():
                print(jsonify(parseGPS(msg)))

except (KeyboardInterrupt,SystemExit):
    print("...Terminated!")
    sys.exit()
