import pydevd_pycharm
import serial
import pynmea2

pydevd_pycharm.settrace('localhost', port=59488, stdoutToServer=True, stderrToServer=True)
def parseGPS(str):
    if str.find('GGA') > 0:
        msg = pynmea2.parse(str)
        print("Timestamp: %s -- Lat: %s %s -- Lon: %s %s -- Altitude:
        %s %s" % (msg.timestamp,msg.lat,msg.lat_dir,msg.lon,msg.lon_dir,msg.altitude,msg.altitude_units))

serialPort = serial.Serial("/dev/ttyS0", 9600, timeout=0.5)

while True:
    str = serialPort.readline()
    parseGPS(str)
