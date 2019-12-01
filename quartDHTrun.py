from quart import Quart, jsonify, render_template_string
import Adafruit_DHT
import asyncio
 
pin = 4 # GPIO pin to which our DHT22 is attached

app = Quart(__name__)
 
@app.route('/')
async def get_humidity_and_temperature_from_DHT11():
    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, pin)
    if humidity is not None and temperature is not None:
        print(f"Sensor says: The temperature returned is now {temperature} deg.F, \n\t\twith a humidity of {humidity} %\n")
        return await render_template_string('{humidity%: {{h}}, temperature_C: {{t}}}', h=humidity, t=temperature)
    else:
        print(f"Try again; sensor didnt respond correctly")
        return await render_template_string('{Try again; sensor didnt respond correctly}')

async def loopy():
    while True:
        print('\nLoop running...\n')
        await asyncio.sleep(3)

#asyncio.get_running_loop().run_in_executor(None, loopy())
asyncio.ensure_future(loopy())
app.run(host='0.0.0.0', port='8888')
