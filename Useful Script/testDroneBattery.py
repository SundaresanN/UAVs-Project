from dronekit import connect

from wireless import Wireless

connection_manager = Wireless()

connection_manager.connect(ssid='SoloLink_GreenDrone', password='Silvestri')

print connection_manager.interface()
print connection_manager.current()
vehicle = connect('udpout:10.1.1.10:14560', wait_ready=True)

#print vehicle.battery
