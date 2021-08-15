from Library import Bluetooth
from btle import BTLEDisconnectError
while(True):
    try:
        # Creates a new bluetooth object based on MAC address of device and the desired characteristic UUID of the device.
        sensor= Bluetooth("e2:24:ee:4f:cb:6a", '00002a63-0000-1000-8000-00805f9b34fb')
        # Connects to device using random connection mode.
        sensor.connect("random")
        # Subscribes to the UUID to be capable on getting notifications later on.
        sensor.subscribe()
        # Waits to recieve the upcoming notifcations.
        sensor.wait()
    # Checks if the device has been disconnected.
    except BTLEDisconnectError:
        print("NOTICE the device has been disconnected, now attempting to reconnect...")
        # Restarts Main.py code
        continue
    finally:
        # Disconnects the device.
        sensor.disconnect()
