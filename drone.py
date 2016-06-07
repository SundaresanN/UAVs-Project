from dronekit import connect, VehicleMode, LocationGlobal, LocationGlobalRelative
from flask import jsonify
import random
from wireless import Wireless
import eventlet
import math
import time

eventlet.monkey_patch()

'''
Initializing the seed of the random class
'''
random.seed(random.random())

class Drone:

	def __init__(self, name, interface, network):

		self.name = name

		self.takeOffAltitude = 5

		self.wifiNetwork = network

		self.networkInterface = interface

		self.listOfLocationsToReach = None
		#self.camera = Camera()

	def connect(self):
		self.vehicle = connect('udpout:10.1.1.10:14560', wait_ready=True)
		self.vehicle.airspeed = 1

	def getCurrentLocation(self):
		location = self.vehicle.location.global_frame
		location = {
			"latitude" : location.lat,
			"longitude" : location.lon,
			"altitude" : self.vehicle.location.global_relative_frame.alt,
		}
		return location

	def getBattery(self):
		return self.vehicle.battery.level

	'''
	This method is used for filling the member listOfLocationsToReach and this gives points
	to reach to drone.
	'''
	def buildListOfLocations(self, locations):
		self.listOfLocationsToReach = list()
		print "Building Location for", self.name
		for location in locations:
			if location != None:
				self.listOfLocationsToReach.append(LocationGlobalRelative(location["latitude"], location["longitude"], location['altitude']))
		print self.listOfLocationsToReach

	'''
	This method is used when someone requires the list of locations to reach in a format that is
	good for other languages that don't have the type LocationGlobalRelative.
	It returns a list of dictionaries and each dictionary is composed of latitude, longitude and altitude.
	'''
	def serializeListOfLocationsToReach(self):
		listToReturn = list()
		for location in self.listOfLocationsToReach:
			location = {
				"latitude" : location.lat,
				"longitude" : location.lon,
				"altitude" : location.alt,
			}
			listToReturn.append(location)
		return listToReturn

	def __handlerTakeOff__(self, signum, frame):
		raise Exception('The take off of ' + self.name + ' is taking too much time, need an abort')

	'''
	Sometimes could happen that the drone is not able to take off, so I must handle this situation and be
	sure that this kind of "blocked situation" doesn't interfere with the flow of the events: I will use a signal that allows me to
	check if drone has been taken off in an amount of seconds.
	(You could do the same with the wifi network connection)
	The "check code" is in the flight function.
	This function is private because I don't want that someone could decide to only taking off, if the drone should consume battery, this consumption must be on flight.
	'''
	def __armAndTakeOff__(self):

		while not self.vehicle.is_armable:
			print "Waiting for vehicle to initialise..."

		self.vehicle.mode = VehicleMode('GUIDED')
		self.vehicle.armed = True

		while not self.vehicle.armed:
			print "Waiting for arming..."

		self.vehicle.simple_takeoff(self.takeOffAltitude)
		#print "self.vehicle.simple_takeoff(self.takeOffAltitude), ", self.takeOffAltitude

	'''
	This method is based on the possibility to send flight news to client via socket.
	This is why I need a Wireless object as parameter and the Socket object.
	The Wireless object is used for switching connection and be sure that the command is sent to right drone
	The Socket object is used for update the location on client side.
	This method will be in concurrency with the other threads, so this is why I will use eventlet.sleep(random.random()) in
	some some points of the code.
	In this function there is the part of code that check if the 'arming and taking off' requires a lot of time and this is
	not possible because I need to be sure that the system will not be blocked because this 'arming and taking off' doesn't work in the right manner
	'''
	def flight(self, connectionManager, socket):
		print "Inside Flight"
		self.__connectToMyNetwork__(connectionManager)
		'''
		This is the part of code where I check if the arm and take require a lot of time
		and the risk is to have a blocked system.
		'''
		'''
		signal.signal(signal.SIGALRM, self.__handlerTakeOff__)
		signal.alarm(5)
		try:
			print "almost inside arm and take off"
			self.__armAndTakeOff__()
		except Exception, exc:
			return exc #if I return exc, this means that I have to notify the client about this issue.
		'''
		print 'self.__armAndTakeOff__()'

		print self.name + " number of locations to reach: ", len(self.listOfLocationsToReach)
		for location in self.listOfLocationsToReach:
			print "Location to reach this time: ", location
			self.__connectToMyNetwork__(connectionManager)
			droneCurrentLocation = self.vehicle.location.global_relative_frame
			#print 'Drone: ' + self.name + ' current location: ', droneCurrentLocation
			distanceToNextLocation = self.__getDistanceFromTwoPointsInMeters__(droneCurrentLocation, location)
			print "self.vehicle.simple_goto(location), ", location
			'''
			Now I have to check the location of the drone in flight, this because dronekit API is thought in order to have
			flight to single point and if I immediatelly send another location to reach, the drone will immediatelly change
			direction of its flight and it will go towards the new location I've just sent.
			'''
			while True:
				eventlet.sleep(self.__generatingRandomSleepTime__())
				self.__connectToMyNetwork__(connectionManager)
				currentDroneLocation = self.vehicle.location.global_relative_frame
				print 'Drone: ' + self.name + ' current location: ', droneCurrentLocation
				remainingDistanceToNextLocation = self.__getDistanceFromTwoPointsInMeters__(currentDroneLocation, location)
				print 'Drone: ' + self.name + ' remaining distance: ', remainingDistanceToNextLocation
				#self.__sendFlightDataToClientUsingSocket__(socket, currentDroneLocation, reached = False, RTLMode = False)

				#If I've just reached the location, I need to take a picture
				if remainingDistanceToNextLocation <= distanceToNextLocation*0.05:
					if self.camera is not None:
						print "Drone " + self.name + " is taking a picture..."
						self.__sendFlightDataToClientUsingSocket__(socket, location, reached = True, RTLMode = False)
						self.camera.takeAPicture(connectionManager)
						# It's time to send the reached status to client
						eventlet.sleep(self.__generatingRandomSleepTime__())
						break
				if self.camera is not None:
					print "Drone " + self.name + " is taking a picture..."
					self.__sendFlightDataToClientUsingSocket__(socket, location, reached = True, RTLMode = False)
					self.camera.takeAPicture(connectionManager)
					# It's time to send the reached status to client
					eventlet.sleep(self.__generatingRandomSleepTime__())
					break

		'''
		Now it's time to come back home
		'''
		print "Removing all the elements in the list of locations to reach"
		self.__removeAllTheElementInTheListOfLocationsToReach__()
		self.__connectToMyNetwork__(connectionManager)
		print "self.vehicle.mode = VehicleMode('RTL')"
		self.__sendFlightDataToClientUsingSocket__(socket, self.vehicle.location.global_frame, reached = False, RTLMode = True)
		#print "self.vehicle.mode = VehicleMode('RTL')"

	'''
	This method is used for flying continuously in two points until drone's battery has reached 20%.
	We have to decide if we need exclusive priority for this kind of flight, so basically I don't wanto to interrupt this
	kind of flight with other request.
	'''
	def twoPointsFlight(self, connectionManager, socket):
		self.__connectToMyNetwork__(connectionManager)
		'''
		signal.signal(signal.SIGALRM, self.__handlerTakeOff__)
		signal.alarm(60)
		try:
			self.__armAndTakeOff__()
		except Exception, exc:
			return exc #if I return exc, this means that I have to notify the client about this issue.
		'''
		print "self.__armAndTakeOff__()"
		'''
		while self.vehicle.location.global_relative_frame.alt <= self.takeOffAltitude:
			print "Drone is taking off..."
		'''
		batteryLimit = 20
		locationBool = False#it means the first location to reach

		while self.vehicle.battery.level >= batteryLimit:

			location = self.listOfLocationsToReach[locationBool]
			droneCurrentLocation = self.vehicle.location.global_relative_frame
			distanceToNextLocation = self.__getDistanceFromTwoPointsInMeters__(droneCurrentLocation, location)
			print "Flying towards location: ", location
			#self.vehicle.simple_goto(location)
			'''
			Waiting drone arrives to this location
			'''
			while True:
				self.__connectToMyNetwork__(connectionManager)
				remainingDistanceToNextLocation = self.__getDistanceFromTwoPointsInMeters__(self.vehicle.location.global_relative_frame, location)
				'''
				If drone has just reached the location, I need to take a picture
				'''
				if remainingDistanceToNextLocation <= distanceToNextLocation * 0.05:
					#I don't know if a picture is required every time drone reaches the location
					#you have to check if camera is not None
					#self.camera.takeAPicture(connectionManager)
					locationBool = not locationBool
					break
				locationBool = not locationBool
				break

		print "Removing locations to reach"
		self.__removeAllTheElementInTheListOfLocationsToReach__(twoLocationsToRemove = True)
		print "self.vehicle.mode = VehicleMode('RTL')"


	'''
	With this function I set up the interface on the value of the this drone instance and after that I give
	priority to the wifi network associated to this drone instance.
	I want this private because is somenthing that I use inside my class and it's not built for a public usage.
	'''
	def __connectToMyNetwork__(self, connectionManager):
		connectionManager.interface(self.networkInterface)
		connectionManager.connect(ssid = self.wifiNetwork, password = "Silvestri")

	'''
	This method produce a number that is the number of seconds that eventlet.sleep() accepts as parameter.
	Again, this function is used inside the class and it's not built for public usage.
	'''
	def __generatingRandomSleepTime__(self):
		number = random.random()*5
		return 3

	'''
	This method has been implemented in order to have a method that given two points of LocationGlobalRelative type,
	it returns the distance between this two points in meters.
	This method is used inside the class and it's not built for public usage
	'''
	def __getDistanceFromTwoPointsInMeters__(self, current, target):
		lat = float(target.lat) - float(current.lat)
		lon = float(target.lon) - float(current.lon)
		return math.sqrt((lat*lat) + (lon*lon)) *  1.113195e5

	'''
	This method allows deleting of the element in the array of locations to reach
	'''
	def __removeAllTheElementInTheListOfLocationsToReach__(self, twoLocationsToRemove = False):
		if twoLocationsToRemove is not True:
			lenght = len(self.listOfLocationsToReach) - 1
			while lenght >= 0:
				del self.listOfLocationsToReach[lenght]
				lenght = lenght - 1
		else:
			print "removing first two elements in the list of locations to reach..."
			del self.listOfLocationsToReach[0]
			del self.listOfLocationsToReach[1]
			print self.listOfLocationsToReach


	def __sendFlightDataToClientUsingSocket__(self, socket, location, reached, RTLMode):
		data = {
			'name' : self.name,
			'location' : [location.lat, location.lon, self.vehicle.location.global_relative_frame.alt],
			'battery' : self.battery.level,
			'reached' : reached,
			'RTL' : RTLMode
		}
		print "Sending data for ", self.name
		socket.emit('Flight Information', data)
		print "Data sent for ", self.name
