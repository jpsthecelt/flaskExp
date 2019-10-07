import json
from flask import Flask
from flask_restplus import Api, Resource, fields

flask_app = Flask(__name__)
app = Api(app = flask_app,
          version = "1.0", 
          title = "GPS Mover",
          description = "Track A-V cart via GPS magic")

name_space = app.namespace('avloc', description='Locate wandering AV cart')
gps_readings = {}

@name_space.route("/")
class MainClass(Resource):
    @app.doc(responses={ 200: 'OK', 400: 'Invalid Argument'}, params={ })
    def get(self):
            try:
                return {
                   "status": "Got new GPS reading; sending to client"
                }

            except Exception as e:
                name_space.abort(400, e.__doc__, status = "Could not retrieve information", statusCode = "400")


    @app.doc(responses={ 200: 'OK', 400: 'Invalid Argument' }, params={ })
    def post(self):
            try:
                pass

            except Exception as e:
                name_space.abort(400, e.__doc__, status = "Could not post configuration", statusCode = "400")

            return {
                "status": "Posted new configuration data"
            }
