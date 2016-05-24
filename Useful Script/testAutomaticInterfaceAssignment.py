
drones = {
	'Solo Green' : ['', ''],
	'Solo Gold': ['', ''],
}
import urllib

def takeAPicture():
	wifipassword = "Silvestri"

	on = "http://10.5.5.9/bacpac/PW?t=" + wifipassword + "&p=%01"
	off = "http://10.5.5.9/bacpac/PW?t=" + wifipassword + "&p=%00"
	shutter = "http://10.5.5.9/bacpac/SH?t=" + wifipassword + "&p=%01"

	opener = urllib.FancyURLopener({})
	f = opener.open(shutter)
	print "Just took a picture"

import string
from wireless import Wireless

connection = Wireless()
print connection.interfaces()

for interface in connection.interfaces():
	print interface
	connection.interface(interface)
	current = connection.current()
	if "Drone" in current:
		for drone in drones:
			droneColor = drone.split()[1]
			if droneColor in current:
				drones[drone][0] = interface
				break
	if "Camera" in current:
 		for drone in drones:
 			droneColor = drone.split()[1]
 			if droneColor in current:
 				drones[drone][1] = interface
 				break

#print drones
import time
for drone in drones:
	print drone + " : ", drones[drone]
	if drones[drone][1] is not '':
		connection.interface(drones[drone][1])
		time.sleep(4)
		print "interface: ", connection.interface()
		#time.sleep(1)
		takeAPicture()

	else:
		print "Camera for " + drone + " is not available"
