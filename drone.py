from dronekit import connect, VehicleMode, LocationGlobal, LocationGlobalRelative, Command
from flask import jsonify
import random
from wireless import Wireless
import eventlet
import math
import time
import threading
from pymavlink import mavutil


'''
Initializing the seed of the random class
'''
random.seed(random.random())

class Drone():

	def __init__(self, name, interface, network):

		#threading.Thread.__init__(self)

		self.name = name

		self.takeOffAltitude = 5

		self.wifiNetwork = network

		self.networkInterface = interface

		self.listOfLocationsToReach = None

		self.fileTest = None

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


	'''
	This function is used for the drone's take off.
	Inside the function, before the end of it, I will wait until drone reaches a "safe" altitude(this because I want to avoid the "grass problem")
	This function is private because I don't want that someone could decide to only taking off, if the drone should consume battery, this consumption must be on flight.
	'''
	def __armAndTakeOff__(self):
		print "Inside take off of ", self.name
		start = time.time()

		end = time.time()
		self.fileTest.write("Take off time required: " + str(end - start) + "\n")

		print self.name + " is taking off..."
		while not self.vehicle.is_armable:
			print "Waiting for vehicle to initialise..."
		self.vehicle.mode = VehicleMode('GUIDED')
		self.vehicle.armed = True
		print self.name + " armed: ", self.vehicle.armed
		while not self.vehicle.armed:
			print "Waiting for arming..."
			time.sleep(1)
		self.vehicle.simple_takeoff(self.takeOffAltitude)
		#print "self.vehicle.simple_takeoff(self.takeOffAltitude), ", self.takeOffAltitude
		'''
		Waiting for a safe altitude for having a flight
		'''
		while True:
			if self.vehicle.location.global_relative_frame.alt <= self.takeOffAltitude*0.8:
				end = time.time()
				self.fileTest.write("Take off time required: " + str(end - start) + "\n")
				return

	'''
	This method is based on the possibility to send live flight information to client via socket.
	This is why I need a Wireless object as parameter and the Socket object.
	The Wireless object is used for switching connection and be sure that the command is sent to right drone
	The Socket object is used for update the location on client side.
	This method will be in concurrency with the other threads, so this is why I will use eventlet.sleep(random.random()) in
	some some points of the code.
	'''
	def missionFlight(self, connectionManager, socket):
		print "Inside Mission Flight ", self.name
		self.fileTest = open("test " + self.name + ".txt", "a")
		print "len: ", len(self.listOfLocationsToReach)
		self.__connectToMyNetwork__(connectionManager)

		cmds = self.vehicle.commands
		cmds.download()
		cmds.wait_ready()
		cmds.clear()
		'''
		I need to decide which take off command I want, MAVLink message or private method built in this class
		'''
		#self.__armAndTakeOff__()
		#adding take off command
		takeOffCmd = Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, 0, self.takeOffAltitude)
		cmds.add(takeOffCmd)

		#adding waypoint and takeAPicture commands
		for location in self.listOfLocationsToReach:
			locationCommand = Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, location.lat, location.lon, location.alt)
			pictureCommand = Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_DO_DIGICAM_CONTROL, 0, 0, 1, 0, 0, 0, 1, 0, 0)
			cmds.add(locationCommand)
			cmds.add(pictureCommand)

		cmds.upload() #sending commands to UAV
		self.vehicle.commands.next = 0 #reset mission set to first(0) waypoint
		start = time.time()
		self.vehicle.mode = VehicleMode('AUTO') #starting the mission
		#writing on the file
		self.fileTest.write("Mission Flight starts on " +  str(time.strftime("%c")))
		self.fileTest.write("\nInitial Battery Level: " +  str(self.getBattery()) + "\n")
		print "Vehicle Mode: " + str(self.vehicle.mode)
		eventlet.sleep(self.__generatingRandomSleepTime__())

		index = 0
		while True:
			self.__connectToMyNetwork__(connectionManager)
			#I'm getting next command from drone in flight
			next = self.vehicle.commands.next
			if next%2!=0:
				next-=1
			while index >= (next/2):
				location == self.listOfLocationsToReach[index]
				#printing in the file
				self.fileTest.write("Location:\n\t- latitude: " + str(location.lat))
				self.fileTest.write("\n\t- longitude: " +  str(location.lon))
				self.fileTest.write("\n\t- altitude: " + str(location.alt))
				self.fileTest.write("\n\t- battery: " + str(self.getBattery()) + "\n")
				#socket
				self.__sendFlightDataToClientUsingSocket__(socket, location, reached = True, RTLMode = False, typeOfSurvey = 'normal', numberOfOscillations = None)
				index+=1

			if index == len(self.listOfLocationsToReach):
				break
			eventlet.sleep(self.__generatingRandomSleepTime__())

		self.__removeAllTheElementInTheListOfLocationsToReach__()
		self.__connectToMyNetwork__(connectionManager)
		self.vehicle.mode = VehicleMode('GUIDED')
		self.vehicle.mode = VehicleMode('RTL')
		end = time.time()
		self.fileTest.write("\nFlight time: " + str(end-start))
		self.fileTest.write("\n###########################################\n")
		self.fileTest.close()
		self.__sendFlightDataToClientUsingSocket__(socket, self.vehicle.location.global_frame, reached = False, RTLMode = True, typeOfSurvey = 'normal', numberOfOscillations = None)
		time.sleep(2)

	def flight(self, connectionManager, socket):
		self.fileTest = open("test " + self.name + ".txt", "a")
		print "Inside Flight ", self.name
		self.__connectToMyNetwork__(connectionManager)

		start = time.time()
		self.fileTest.write("Flight starts on " +  str(time.strftime("%c")))
		self.fileTest.write("\nInitial Battery Level: " +  str(self.getBattery()))
		self.fileTest.write("\n")

		self.__armAndTakeOff__()
		eventlet.sleep(self.__generatingRandomSleepTime__())

		print self.name + " number of locations to reach: ", len(self.listOfLocationsToReach)
		for location in self.listOfLocationsToReach:
			print "Location to reach this time: ", location
			self.__connectToMyNetwork__(connectionManager)
			droneCurrentLocation = self.vehicle.location.global_relative_frame
			distanceToNextLocation = self.__getDistanceFromTwoPointsInMeters__(droneCurrentLocation, location)
			print "self.vehicle.simple_goto(location), ", location
			#self.vehicle.simple_goto(location)
			'''
			Now I have to check the location of the drone in flight, this because dronekit API is thought in order to have
			flight to single point and if I immediatelly send another location to reach, the drone will immediatelly change
			direction of its flight and it will go towards the new location I've just sent.
			'''
			while True:
				print "Checking distance from location to reach..."
				tollerance = 1
				eventlet.sleep(self.__generatingRandomSleepTime__())
				self.__connectToMyNetwork__(connectionManager)
				currentDroneLocation = self.vehicle.location.global_relative_frame
				print 'Drone: ' + self.name + ' current location: ', droneCurrentLocation
				remainingDistanceToNextLocation = self.__getDistanceFromTwoPointsInMeters__(currentDroneLocation, location)
				print 'Drone: ' + self.name + ' remaining distance: ', remainingDistanceToNextLocation
				#self.__sendFlightDataToClientUsingSocket__(socket, currentDroneLocation, reached = False, RTLMode = False, 'normal', None)
				#If I've just reached the location, I need to take a picture
				if remainingDistanceToNextLocation <= distanceToNextLocation*tollerance:
					print "Drone " + self.name + " is taking a picture..."
					#self.__takeAPicture__()
					self.fileTest.write("Location:\n\t- latitude: " + str(location.lat))
					self.fileTest.write("\n\t- longitude: " +  str(location.lon))
					self.fileTest.write("\n\t- altitude: " + str(location.alt))
					self.fileTest.write("\n\t- battery: " + str(self.getBattery()) + "\n")
					self.__sendFlightDataToClientUsingSocket__(socket, location, reached = True, RTLMode = False, typeOfSurvey = 'normal', numberOfOscillations = None)
					break

		'''
		Now it's time to come back home
		'''
		print "Removing all the elements in the list of locations to reach"
		self.__removeAllTheElementInTheListOfLocationsToReach__()
		self.__connectToMyNetwork__(connectionManager)
		print "self.vehicle.mode = VehicleMode('RTL')"
		end = time.time()
		self.fileTest.write("\nFlight time: " + str(end-start))
		self.fileTest.write("\n###########################################\n")
		self.fileTest.close()
		self.__sendFlightDataToClientUsingSocket__(socket, self.vehicle.location.global_frame, reached = False, RTLMode = True, typeOfSurvey = 'normal', numberOfOscillations = None)
		time.sleep(2)

	'''
	This method is used for flying continuously in two points until drone's battery reaches 20%.
	We have to decide if we need exclusive priority for this kind of flight, so basically I don't wanto to interrupt this
	kind of flight with other request.
	'''
	def oscillationFlight(self, connectionManager, socket):
		self.fileTest = open("test " + self.name + ".txt", "a")
		#I need to know if I have two differnt locations in terms of lat, lon and alt or I have same locations but with differnt altitude
		sameLocation = self.listOfLocationsToReach[0].lat == self.listOfLocationsToReach[1].lat and self.listOfLocationsToReach[0].lon == self.listOfLocationsToReach[1].lon
		if sameLocation is True:
			print "Same location but different altitude"
		#self.__connectToMyNetwork__(connectionManager)
		start = time.time()
		self.fileTest.write("Oscillation Flight starts on " +  str(time.strftime("%c")))
		self.fileTest.write("\nInitial Battery Level: " + str(self.getBattery()))
		self.__armAndTakeOff__()
		time.sleep(2)
		batteryLimit = 84
		locationBool = False #it means the first location to reach
		numberOfOscillations = 0

		while self.vehicle.battery.level >= batteryLimit:
			print "Battery: ", self.vehicle.battery.level
			location = self.listOfLocationsToReach[locationBool]
			droneCurrentLocation = self.vehicle.location.global_relative_frame
			distanceToNextLocation = self.__getDistanceFromTwoPointsInMeters__(droneCurrentLocation, location)
			#writing on the log file
			self.fileTest.write("Location:\n\t- latitude: " + str(location.lat))
			self.fileTest.write("\n\t- longitude: " + str(location.lon))
			self.fileTest.write("\n\t- altitude: " + str(location.alt))
			self.fileTest.write("\n\t- battery: " + str(self.getBattery()) + "\n")

			print "Flying towards location: ", location
			self.vehicle.simple_goto(location)
			'''
			Waiting drone arrives to this location
			'''
			while True:
				time.sleep(5)
				'''
				If drone has just reached the location(even if there are same locations or not), I need go to the other location
				'''
				print "Checking distance from location to reach..."
				if sameLocation == True:
					print "Same location flight"
					altitudeToReach = location.alt
					if self.vehicle.location.global_relative_frame.alt <= altitudeToReach*0.95:
						locationBool = not locationBool
						if locationBool == 0:
							numberOfOscillations = numberOfOscillations + 1
						break
				else:
					tollerance = 0.1
					remainingDistanceToNextLocation = self.__getDistanceFromTwoPointsInMeters__(self.vehicle.location.global_relative_frame, location)
					if remainingDistanceToNextLocation <= distanceToNextLocation * tollerance:
						print "Changing location to reach for the oscillation flight"
						locationBool = not locationBool
						if locationBool == 0:
							numberOfOscillations = numberOfOscillations + 1
						break

		print "Removing locations to reach"
		self.__removeAllTheElementInTheListOfLocationsToReach__(twoLocationsToRemove = True)
		self.vehicle.mode = VehicleMode('RTL')
		end = time.time()
		self.fileTest.write("\nNumber of oscillations: " + str(numberOfOscillations))
		self.fileTest.write("\nFlight time: " + str(end-start))
		self.fileTest.write("\n###########################################\n")
		self.fileTest.close()
		return {
			'name' : self.name,
			'battery' : self.vehicle.battery.level,
			'oscillations' : numberOfOscillations
			}


	def missionOscillationFlight(self):
		self.fileTest = open("test " + self.name + ".txt", "a")

		self.__armAndTakeOff__()
		cmds = self.vehicle.commands
		cmds.download()
		cmds.wait_ready()
		cmds.clear()
		for value in xrange(0, 200):
			#even
			if value%2 == 0:
				locationCommand = Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, self.listOfLocationsToReach[0].lat, self.listOfLocationsToReach[0].lon, self.listOfLocationsToReach[0].alt)
			#odd
			else:
				locationCommand = Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, self.listOfLocationsToReach[1].lat, self.listOfLocationsToReach[1].lon, self.listOfLocationsToReach[1].alt)
			cmds.add(locationCommand)
		cmds.upload() #sending commands to UAV
		self.vehicle.commands.next = 0 #reset mission set to first(0) waypoint
		start = time.time() #starting timer
		self.vehicle.mode = VehicleMode('AUTO') #starting the mission
		#writing on the file
		self.fileTest.write("Mission Flight starts on " +  str(time.strftime("%c")))
		self.fileTest.write("\nInitial Battery Level: " +  str(self.getBattery()) + "\n")
		numberOfOscillations = 0
		batteryLimit = 20
		while self.vehicle.battery.level >= batteryLimit:
			next = self.vehicle.commands.next
			print "Next command index: ", next
			print "Next: ", self.vehicle.commands[next]
			if next%2 == 0 and next > 1:
				numberOfOscillations += 1

			location = self.vehicle.location.global_relative_frame
			self.fileTest.write("Location:\n\t- latitude: " + str(location.lat))
			self.fileTest.write("\n\t- longitude: " + str(location.lon))
			self.fileTest.write("\n\t- altitude: " + str(location.alt))
			self.fileTest.write("\n\t- battery: " + str(self.getBattery()) + "\n")
			time.sleep(2)

		print "Removing locations to reach"
		self.__removeAllTheElementInTheListOfLocationsToReach__(twoLocationsToRemove = True)
		self.vehicle.mode = VehicleMode('GUIDED')
		self.vehicle.mode = VehicleMode('RTL')
		end = time.time()
		self.fileTest.write("\nNumber of oscillations: " + str(numberOfOscillations))
		self.fileTest.write("\nFlight time: " + str(end-start))
		self.fileTest.write("\n###########################################\n")
		self.fileTest.close()
		return {
			'name' : self.name,
			'battery' : self.vehicle.battery.level,
			'oscillations' : numberOfOscillations
			}


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
		return number

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
			lenght = len(self.listOfLocationsToReach) - 1
			while lenght >= 0:
				del self.listOfLocationsToReach[lenght]
				lenght = lenght - 1

	def __sendFlightDataToClientUsingSocket__(self, socket, location, reached, RTLMode, typeOfSurvey, numberOfOscillations):
		if typeOfSurvey == 'normal':
			data = {
				'name' : self.name,
				'location' : [location.lat, location.lon, self.vehicle.location.global_relative_frame.alt],
				'battery' : self.vehicle.battery.level,
				'reached' : reached,
				'RTL' : RTLMode
			}
			print "Sending data for ", self.name
			socket.emit('Flight Information ' + self.name, data)
			print "Data sent for ", self.name
			time.sleep(1)
			return

		if typeOfSurvey == 'oscillation':
			data = {
				'name' : self.name,
				'battery' : self.vehicle.battery.level,
				'oscillations' : numberOfOscillations
			}
			print "Sending data for ", self.name
			socket.emit('Oscillation Survey Data', data)
			print "Data sent for ", self.name
			time.sleep(1)
			return

	def __takeAPicture__(self):
		msg = self.vehicle.message_factory.gopro_set_request_encode(1, 154, mavutil.mavlink.GOPRO_COMMAND_SHUTTER, (1, 0, 0, 0))
		self.vehicle.send_mavlink(msg)
		self.vehicle.commands.upload()
