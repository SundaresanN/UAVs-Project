import string 

conn = "SoloGoldDrone"
conn2 = "SoloGoldCameraRGB"

conn3= "SoloGreenDrone"
conn4= "SoloGreenCameraRGB"

interfaces = {
	'a': conn,
	'b': conn3,
	'c': conn2,
	'd': conn4
}

drones = {
	'Solo Gold': ['', ''],
	'Solo Green': ['', '']
}
for interface in interfaces:
	print 'Interface: ', interface
	currentConn = interfaces[interface]
	if "Drone" in currentConn:
		for drone in drones:
			droneColor = drone.split()[1]
			if droneColor in currentConn:
				drones[drone][0] = interface
				print "I'm breaking the nested for"
				break
	if 'Camera' in currentConn:
		for drone in drones:
			droneColor = drone.split()[1]
			if droneColor in currentConn:
				drones[drone][1] = interface
				print "I'm breaking the nested for"
				break

print drones

