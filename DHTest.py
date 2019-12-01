import time
import board
import Adafruit_DHT

# Initial the dht device, with data pin connected to:
pin = 4 # GPIO#4 for our rPi0
sensor = Adafruit_DHT.AM2302
#dhtDevice = adafruit_dht.DHT22(board.D4)

while True:
   try:
       humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
      # Print the values to the serial port
#      temperature_c = dhtDevice.temperature
#      temperature_f = temperature_c * (9 / 5) + 32
#      humidity = dhtDevice.humidity
       if humidity is not None and temperature is not None:
#          print("Temp: {:.1f} F / {:.1f} C    Humidity: {}% ")
          print("Temp: {:.1f} C    Humidity: {:.2f}% "
             .format(temperature, humidity))
       else:
          print('Failed to get reading. Try again!')

   except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
#        print(error.args[0])
       print('Whoops! error; try, again')

   time.sleep(2.0)

