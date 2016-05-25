from wireless import Wireless
from drone import Drone
from dronekit import connect, VehicleMode
from flask_socketio import SocketIO, emit, send
import eventlet
import time
import math
import urllib #I need this for camera

class ServerBrain:

	def __init__(self, socket = None):

		self.socket = socket
		self.dronesName = ["Solo Gold", "Solo Green"]

		self.wifiConnections = {
			'Solo Gold' : ['SoloLink_gold', 'sololinkmst'],
			'Solo Green' : ['SoloLink_MST', 'sololinkmst']
		}
		self.droneWiFiInterfaces = {
			'Solo Gold' : "wlx40a5ef03ea3a",
			'Solo Green' : "wlx40a5ef040181"
		}
		#used to switch connection
		self.conn = Wireless()

		#array of drone initializer
		self.drones = {
			'Solo Gold' : Drone('Solo Gold', ['SoloLink_gold', 'sololinkmst'], ['mstgorgbgold', 'Silvestri']),
			'Solo Green' : Drone('Solo Green', ['SoloLink_MST', 'sololinkmst'], ['mstgorgbgreen', 'Silvestri'])
		}

	def switchConnection(self, droneName, type):
		ssid = password = ""
		if type == "drone":
			ssid = self.drones[droneName].wifiConnection[0]
			password = self.drones[droneName].wifiConnection[1]
		else:
			ssid = self.drones[droneName].cameraConnection[0]
			password = self.drones[droneName].cameraConnection[1]
		print "I'm switching WiFi connection for ", type
		return self.conn.connect(ssid=ssid, password=password)

	def takeAPicture(self, name):

		self.switchConnection(name, "camera")

		wifipassword = "09021967"

		on = "http://10.5.5.9/bacpac/PW?t=" + wifipassword + "&p=%01"
		off = "http://10.5.5.9/bacpac/PW?t=" + wifipassword + "&p=%00"
		shutter = "http://10.5.5.9/bacpac/SH?t=" + wifipassword + "&p=%01"

		opener = urllib.FancyURLopener({})
		f = opener.open(shutter)
		print "Just took a picture"

	def connectDrone(self, droneName):

		if self.conn.current() != self.wifiConnections[droneName]:
			if self.switchConnection(droneName, "drone") == False:
				#self.conn.power(False) #this command sets off the WiFi antenna
				return droneName + " network is not reacheale"

		self.drones[droneName].connect()
		location = self.drones[droneName].getActualLocation()

		return location

	def activateThread(self, functionName, name, listOfLocations):

		if functionName == "flight":
			eventlet.spawn(self.flight, listOfLocations, name)

	def getDistanceMeters(self, current, target):
		lat = float(target.lat) - float(current.lat)
		lon = float(target.lon) - float(current.lon)
		return math.sqrt((lat*lat) + (lon*lon)) *  1.113195e5

	def arm(self, name):

		#print "Arming... ", name
		self.switchConnection(name, "drone")
		self.drones[name].vehicle = connect('udpout:10.1.1.10:14560', wait_ready=True)

		#print "Current WiFi network: ", self.conn.current()

		#print "Vehicle of " + name + " is: ", self.drones[name].vehicle is not None

		#print name + " is armable: ", self.drones[name].vehicle.is_armable
		while not self.drones[name].vehicle.is_armable:
			print "Waiting for vehicle to initialise..", name

		self.drones[name].vehicle.mode = VehicleMode("GUIDED")
		self.drones[name].vehicle.armed = True

		#print name + " armed: ", self.drones[name].vehicle.armed
		while not self.drones[name].vehicle.armed:
			print "Waiting for arming ", name
			time.sleep(1)
		#print "I finish the arm function execution and I'm ready to take off, ", name

	'''
	def flight(self, listOfLocations, name):
		print "Inside flight function, ", name
		self.switchConnection(name, "drone")
		self.drones[name].buildListOfLocations(listOfLocations)

		print self.drones[name].listOfLocations
		eventlet.sleep(3)
		i = 0
		for locationToReach in self.drones[name].listOfLocations:
			self.switchConnection(name, "drone")
			print "Location to reach for " + name + " is ", locationToReach
			soloCurrentLocation = self.drones[name].vehicle.location.global_relative_frame
			print name + " index: ", i
			i = i + 1
			#print locationToReach
			targetDistance = self.getDistanceMeters(soloCurrentLocation, locationToReach)
			print targetDistance
			print "Sto inviando, ", name

			self.socket.emit('Update Live Location', {
					"name": name,
					"status": "reached",
					"latitude": locationToReach.lat,
					"longitude": locationToReach.lon
					#"distance": targetDistance
					})

			self.takeAPicture(name)
			eventlet.sleep(5)

		print "Sono uscito, ", name
	'''
	def flight(self, listOfLocations, name):
		locationBool=True
		batteryLimit=20
		print "I'm " + name + " and I'm inside flight function"

		self.arm(name)
		targetAltitude = 5
		self.drones[name].vehicle.simple_takeoff(targetAltitude)

		while message["reached"] == False:
			eventlet.sleep(2)
			print "I'm trying to understand if I reach the target altitude ", name
			self.switchConnection(name, "drone")
			message = {"reached": False , "altitude": self.drones[name].vehicle.location.global_relative_frame.alt, "name" : name}
			if self.drones[name].vehicle.location.global_relative_frame.alt >= targetAltitude*0.90:
				message = {"reached": True , "altitude": targetAltitude, "name" : name}
				#self.drones[name].vehicle.mode = VehicleMode('RTL')
			#self.socket.emit('Altitude Reached', message)

		eventlet.sleep(3)

		self.drones[name].buildListOfLocations(listOfLocations)
		print self.drones[name].listOfLocations

		while self.drones[name].vehicle.battery.level >= batteryLimit:
			eventlet.sleep(5)
			self.switchConnection(name, "drone")
			locationToReach=listOfLocations[locationBool]
			#connecting again the vehicle to be sure that the command will be sent
			self.drones[name].vehicle = connect('udpout:10.1.1.10:14560', wait_ready=True)

			print "Location to reach for " + name + " is ", locationToReach
			soloCurrentLocation = self.drones[name].vehicle.location.global_relative_frame
			targetDistance = self.getDistanceMeters(soloCurrentLocation, locationToReach)
			self.drones[name].vehicle.simple_goto(self.drones[name].locationToReach)

			#Right here I'm waiting that drone reaches each location on the list
			while status != "reached":
				eventlet.sleep(2)
				self.switchConnection(name, "drone")

				soloCurrentLocation = self.drones[name].vehicle.location.global_relative_frame
				remainingDistance = self.getDistanceMeters(soloCurrentLocation, locationToReach)
				status = "flying"
				if remainingDistance <= targetDistance * 0.05:
					#here the code for taking picture
					#self.takeAPicture(name)
					status = "reached"

					self.socket.emit('Update Live Location', {
					"name": name,
					"status": status,
					"latitude" : locationToReach.lat,
					"longitude" : locationToReach.lon,
					"altitude" : locationToReach.alt,
					})
					locationBool= not locationBool
				'''
				self.socket.emit('Update Live Location', {
					"name": name,
					"status": status,
					"latitude" : soloCurrentLocation.lat,
					"longitude" : soloCurrentLocation.lon,
					"altitude" : soloCurrentLocation.alt,
					})
				'''

		
		self.switchConnection(name, "drone")
		#connecting again the vehicle to be sure that the command will be sent
		self.drones[name].vehicle = connect('udpout:10.1.1.10:14560', wait_ready=True)
		self.drones[name].vehicle.mode = VehicleMode('RTL')
