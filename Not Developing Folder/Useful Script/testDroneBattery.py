
from dronekit import connect
from pymavlink import mavutil
from wireless import Wireless

connection_manager = Wireless()
connection_manager.interface('wlan1')


connection_manager.connect(ssid='SoloLink_GreenDrone', password='Silvestri')

print connection_manager.interface()
print connection_manager.current()
vehicle = connect('udpout:10.1.1.10:14560', wait_ready=True)
print vehicle.battery

connection_manager.interface('wlan0')
connection_manager.connect(ssid='SoloLink_GoldDrone', password='Silvestri')
print connection_manager.interface()
print connection_manager.current()
vehicleTwo = connect('udpout:10.1.1.10:14560', wait_ready=True)
print vehicleTwo.battery
connection_manager.interface('wlan1')
connection_manager.connect(ssid='SoloLink_GreenDrone', password='Silvestri')

print vehicle.battery
