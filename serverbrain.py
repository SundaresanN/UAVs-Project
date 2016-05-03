from wireless import Wireless
import drone
from dronekit import connect, VehicleMode
from flask_socketio import SocketIO, emit, send
import eventlet
import time
import math

class ServerBrain:

	def __init__(self, socket = None):
		
		self.socket = socket
		
		self.dronesName = ["Solo Gold", "Solo Green"]
		self.wifiConnections = {
			'Solo Gold' : ['SoloLink_gold', 'sololinkmst'],
			'Solo Green' : ['SoloLink_MST', 'sololinkmst']
		}
		#used to switch connection
		self.conn = Wireless()
		#array of drones initializer
		self.drones = {
			'Solo Gold' : drone.Drone('Solo Gold', self.wifiConnections['Solo Gold']),
			'Solo Green' : drone.Drone('Solo Green', self.wifiConnections['Solo Green'])
		}

	def getDistanceMeters(firstLocation, secondLocation):
		latitude = float(secondLocation.lat) - float(firstLocation.lat)
		longitude = float(secondLocation.lon) - float(firstLocation.lon)
		return math.sqrt((latitude*latitude) + (longitude*longitude))*1.113195e5

	def switchConnection(self, droneName):
		print "I'm going to switch WiFi connection, ", droneName
		return self.conn.connect(ssid=self.drones[droneName].wifiConnection[0], password=self.drones[droneName].wifiConnection[1])
		
	def connectDrone(self, droneName):
		
		if self.conn.current() != self.wifiConnections[droneName]:
			if self.switchConnection(droneName) == False:
				#self.conn.power(False) #this command sets off the WiFi antenna
				return droneName + " netwotk is not reacheble"
		
		self.drones[droneName].connect()
		location = self.drones[droneName].getActualLocation()
		
		return location

	def activateThread(self, functionName, name, listOfLocations):

		if functionName == "flight":
			eventlet.spawn(self.flight, listOfLocations, name)
	
	def arm(self, name):

		print "Arming... ", name
		self.switchConnection(name)
		self.drones[name].vehicle = connect('udpout:10.1.1.10:14560', wait_ready=True)
		
		print "Current WiFi network: ", self.conn.current()
		
		print "Vehicle of " + name + " is: ", self.drones[name].vehicle is not None
		
		print name + " is armable: ", self.drones[name].vehicle.is_armable
		while not self.drones[name].vehicle.is_armable:
			print "Waiting for vehicle to initialise..", name
			
		self.drones[name].vehicle.mode = VehicleMode("GUIDED")
		self.drones[name].vehicle.armed = True

		print name + " armed: ", self.drones[name].vehicle.armed
		while not self.drones[name].vehicle.armed:
			print "Waiting for arming ", name
			time.sleep(1)
		print "I finish the arm function execution and I'm ready to take off, ", name

	def flight(self, listOfLocations, name):
		print "I'm " + name + " and I'm inside flight function"
		
		self.arm(name)
		targetAltitude = 2
		self.drones[name].vehicle.simple_takeoff(targetAltitude)
		
		eventlet.sleep(5)
		
		while True:
			print "I'm trying to understand if I reach the target altitude ", name
			eventlet.sleep(3)
			self.switchConnection(name)
			message = {"reached": False , "altitude": self.drones[name].vehicle.location.global_relative_frame.alt, "name" : name}
			if self.drones[name].vehicle.location.global_relative_frame.alt >= targetAltitude*0.95:
				message = {"reached": True , "altitude": targetAltitude, "name" : name}
				self.drones[name].vehicle.mode = VehicleMode('RTL')
			self.socket.emit('Altitude Reached', message)
			if message["reached"] == True:
				break

		eventlet.sleep(3)

		self.drones[name].buildListOfLocations(listOfLocations)

		for locationToReach in listOfLocations:
			eventlet.sleep(3)
			self.switchConnection(name)
			#self.drones[name].vehicle = connect('udpout:10.1.1.10:14560', wait_ready=True)
			print "Location to reach for " + name + " is ", locationToReach
			soloCurrentLocation = vehicle.location.global_relative_frame
			targetDistance = self.getDistanceMeters(soloCurrentLocation, locationToReach)
			self.drones[name].vehicle.simple_goto(locationToReach)
			eventlet.sleep(2)
			while True:
				self.switchConnection(name)
				soloCurrentLocation = self.drones[name].vehicle.global_relative_frame
				remainingDistance = self.getDistanceMeters(soloCurrentLocation, targetDistance)
				socketio.emit('Update Live Location', {
					"name": name,
					"status": "flying",
					"latitude" : soloCurrentLocation.lat,
					"longitude" : soloCurrentLocation.lon, 
					"altitude" : soloCurrentLocation.alt,
					})
				if remainingDistance <= targetDistance * 0.05:
					#here the code for taking picture
					socketio.emit('Update Live Location', {
					"name": name,
					"status": "reached"
					})
					break
				eventlet.sleep(2)
		#self.drones[name].vehicle = connect('udpout:10.1.1.10:14560', wait_ready=True)
		self.drones[name].vehicle.mode = VehicleMode('RTL')









		