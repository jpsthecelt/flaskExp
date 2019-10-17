import sys
import serial
import pynmea2
import json
import time
from collections import deque
import argparse

# Given an NMEA input string (from attached GPS device), parse and either return it's T/S, 
#       alt, lat/lon, etc (as a JSON dict) from the GGA message, add message-type to the 
#       discardQ (based on command-line 'verbose' switch), finally returning JSON dict message), 
#       or else return parse-error message.
def parseGPS(rawMesg, discardIt):
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
        if discardIt:
            return (f"{{Discarded: {msg.sentence_type}}}")
        else:
            return ("")
    else:
        # (recall that gps_qual == 0 is 'no fix', or fix=False, 1 == fix, 2-5 are fix-other)
        fix = msg.gps_qual == 1 
        return (f"{{Timestamp: {msg.timestamp}, Lat: {msg.lat or 0.0} {msg.lat_dir} ,  Lon: {msg.lon or 0.0} {msg.lon_dir}, Altitude: {msg.altitude or 0.0} {msg.altitude_units or 'm'} Fix: {fix} Satellites: {msg.gps_num_sats or 0}}}")


try:
    QMAX = 100
    discardQ = deque(maxlen=QMAX)
    # Initialize discardQ list and and serial-inpuyt channel; clearing out any 'framing errors' in receiving-channel 
    #            (we chose to clear out 5 of them)
    parser = argparse.ArgumentParser(description='Grab and display incoming GPS messages via flask website')
    parser.add_argument('-v', default=False, action='store_true', help='print all discarded messages ')
    results = parser.parse_args()

    with serial.Serial("/dev/serial0", 9600, timeout=0.5) as gIn:
        [print("Synchronizing...: {}".format(gIn.readline().decode('ascii', errors='replace'))) for i in range(5)]
            
        # Then, while it is possible to read messages from the serial-input, read & parse input data
        #       printing out result
        while True:
            print(parseGPS(gIn.readline().decode('ascii', errors='replace'), results.v))
            time.sleep(1)

# process any system-exit errors or ^c received, outputting our discardQ contents 'before we go'
except (KeyboardInterrupt,SystemExit):
    print("...Terminated!")
    print(f"Last {len(discardQ)} discarded messages were {discardQ}")
    sys.exit()
