from flask import Flask, jsonify
import Adafruit_DHT
 
app = Flask(__name__)
 
@app.route('/')
def get_humidity_and_temperature_from_DHT11():
    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, 4)
    print(f"The temperature is now {temperature} deg.F, with a humidity of {humidity} %")
    return jsonify({'humidity%': humidity, 'temperature_F': temperature})
 
app.run(host='0.0.0.0', port='8888')
