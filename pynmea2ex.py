import sys
import serial
import pynmea2

def parseGPS(bites):
    str = bites.decode()
    if str.find('GGA') > 0:
        msg = pynmea2.parse(str)
        print("Timestamp: %s -- Lat: %s %s -- Lon: %s %s -- Altitude: %s %s" % 
              (msg.timestamp,msg.lat,msg.lat_dir,msg.lon,msg.lon_dir,msg.altitude,msg.altitude_units))

try:
    serialPort = serial.Serial("/dev/serial0", 9600, timeout=0.5)

    while True:
        str = serialPort.readline()
        parseGPS(str)

except (KeyboardInterrupt,SystemExit):
    print("...Terminated!")
    sys.exit()
