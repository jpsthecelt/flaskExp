import uasyncio as asyncio
import as_GPS
from machine import UART
def callback(gps, *_):  # Runs for each valid fix
    print(gps.latitude(), gps.longitude(), gps.altitude)

uart = UART(4, 9600)
sreader = asyncio.StreamReader(uart)  # Create a StreamReader
gps = as_GPS.AS_GPS(sreader, fix_cb=callback)  # Instantiate GPS

async def test():
    print('waiting for GPS data')
    await gps.data_received(position=True, altitude=True)
    await asyncio.sleep(60)  # Run for one minute
loop = asyncio.get_event_loop()
loop.run_until_complete(test())
