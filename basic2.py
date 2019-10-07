import os
from typing import Type

from gps import *
from time import *
import time
import threading

from collections import namedtuple

from flask import Flask
from flask_restplus import Api, Resource

flask_app = Flask(__name__)
app = Api(app=flask_app)

gpsd = None  # setting the global variable
gd = None
# os.system('clear')  # clear the terminal (optional)

Gd = namedtuple( 'Gd', 'lat long time alt eps epx epv ept ms_speed climb track mode sats' )

name_space = app.namespace('main', description='API Description (swagger) ')


@name_space.route("/")
class MainClass(Resource):
    def get(self):
        return {
            "status": "Got new GPS data:\n"+
            json.dumps(gd._asdict())
        }

    def post(self):
        return {
            "status": "Posted new GPS command/data"
        }


class GpsPoller(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        global gpsd  # bring it in scope
        global gd
        gpsd = gps(mode=WATCH_ENABLE)  # starting the stream of info
        self.current_value = None
        self.running = True  # setting the thread running to true

    def run(self):
        global gpsd
        global gd
        while gpsp.running:
            gd = gpsd.next()  # this will continue to loop and grab EACH set of gpsd info to clear the buffer


if  __name__ == '__main__':
    gpsp = GpsPoller()  # create the thread
    try:
        gpsp.start()  # start it up
        # while True:
            # It may take a second or two to get good data
            # print( gpsd.fix.latitude,', ',gpsd.fix.longitude,'  Time: ',gpsd.utc

            # os.system('clear')

        gd = Gd(
            gpsd.fix.latitude, gpsd.fix.longitude,
            '%s' % gpsd.utc + gpsd.fix.time,
            gpsd.fix.altitude,
            gpsd.fix.eps, gpsd.fix.epx, gpsd.fix.epv, gpsd.fix.ept,
            gpsd.fix.speed,
        gpsd.fix.climb, gpsd.fix.track,
        gpsd.fix.mode,
        gpsd.satellites
        )

        print()
        print(' GPS reading')
        print('----------------------------------------')
        print('latitude    ', gpsd.fix.latitude)
        print('longitude   ', gpsd.fix.longitude)
        print('time utc    ', gpsd.utc, ' + ', gpsd.fix.time)
        print('altitude (m)', gpsd.fix.altitude)
        print('eps         ', gpsd.fix.eps)
        print('epx         ', gpsd.fix.epx)
        print('epv         ', gpsd.fix.epv)
        print('ept         ', gpsd.fix.ept)
        print('speed (m/s) ', gpsd.fix.speed)
        print('climb       ', gpsd.fix.climb)
        print('track       ', gpsd.fix.track)
        print('mode        ', gpsd.fix.mode)
        print()
        print('sats        ', gpsd.satellites)

        time.sleep(5)  # set to whatever

    except (KeyboardInterrupt, SystemExit):  # when you press ctrl+c
        print("\nKilling Thread...")
        gpsp.running = False
        gpsp.join()  # wait for the thread to finish what it's doing

    print("Done.\nExiting.")
