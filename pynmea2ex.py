import sys
import serial
import pynmea2
import json

def parseGPS(str):
    if str.find('GGA') > 0:
        msg = pynmea2.parse(str)
#        print("Timestamp: %s -- Lat: %s %s -- Lon: %s %s -- Altitude: %s %s" % 
#              (msg.timestamp,msg.lat,msg.lat_dir,msg.lon,msg.lon_dir,msg.altitude,msg.altitude_units))
        return json.dumps(("Timestamp: %s -- Lat: %s %s -- Lon: %s %s -- Altitude: %s %s" % 
                  (msg.timestamp,msg.lat,msg.lat_dir,msg.lon,msg.lon_dir,msg.altitude,msg.altitude_units)),indent=4)

#serialPort = serial.Serial("/dev/ttyS0", 9600, timeout=0.5)
#
#while True:
#    str = serialPort.readline()
#    parseGPS(str)

try:
    with serial.Serial("/dev/serial0", 9600, timeout=0.5) as gIn:
    while True:
        str = gIn.readline().decode()
        for msg in gStream.next():
            print(parseGPS(str))

except (KeyboardInterrupt,SystemExit):
    print("...Terminated!")
    sys.exit()
