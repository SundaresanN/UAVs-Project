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

	'''
	This method creates a connection with the real Solo.
	'''
	def connect(self):
		try:
			self.vehicle = connect('udpout:10.1.1.10:14560', wait_ready=True)
			self.__cleaningMissionsFromSoloMemory__()
		except Exception as e:
			print "Connection error.."
			raise

		'''self.vehicle = connect('udpout:10.1.1.10:14560', wait_ready=True)
		print "cleaning commands for " + self.name
		cmds = self.vehicle.commands
		cmds.download()
		time.sleep(30)
		cmds.wait_ready()
		print "There are " + str(len(cmds)) + " commands into the Solo's memory 2"
		cmds.clear()
		#self.__cleaningMissionsFromSoloMemory__()
		#print self.name + " has cleaned its commands."'''

	'''
	This method returns the current Solo's location in a dictionary.
	'''
	def getCurrentLocation(self):
		location = self.vehicle.location.global_frame
		location = {
			"latitude" : location.lat,
			"longitude" : location.lon,
			"altitude" : self.vehicle.location.global_relative_frame.alt,
		}
		return location
	'''
	This method returns the level of the battery of the current Solo.
	'''
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
	This method allows the taking off of the Solo.
	A check on the altitude reached by the Solo during the taking off will be made until Solo reaches a 'safe' altitude.
	'''
	def __armAndTakeOff__(self):
		print "Inside take off of ", self.name
		start = time.time()
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
		'''
		Waiting for a safe altitude for having a flight
		'''
		while True:
			if self.vehicle.location.global_relative_frame.alt <= self.takeOffAltitude*0.8:
				end = time.time()
				self.fileTest.write("Take off time required: " + str(end - start) + "\n\n")
				return

	'''
	This method allows the drone's flight. It can not allow a perfect accuracy with live information on client side.
	This lack of accuracy is due to the use of uploading commands into the Solo's memory.
	We can identify 3 blocks:
	1. Uploading the commands into Solo's memory and take off
	2. Checking what is the next command the Solo has to execute and understanding in which location the Solo has flown
	   and so updating the information on client side via socket
	3. Clearing all the data structures used for this flight and sending command for coming back home to the Solo
	In the meantime of the execution of this method, a file will be updated with the information about location, battery level and time passed
	of the current flight.
	'''
	def flightWithTheUsingOfSolosMemory(self, connectionManager, socket):

		print "Mission Flight for ", self.name
		self.fileTest = open("Riccardo test " + self.name + ".txt", "a")
		self.__connectToMyNetwork__(connectionManager)
		#writing on the file
		self.fileTest.write("Mission Flight starts on " +  str(time.strftime("%c")) + '\n')
		'''
		UPLOADING COMMANDS INTO THE SOLO'S MEMORY
		'''
		self.__uploadCommandsIntoSoloMemory__()
		socket.emit('Take off ack', self.name + " has just taken off. Now it is ready to start the mission.")
		eventlet.sleep(self.__generatingRandomSleepTime__())

		'''
		STARTING THE MISSION, CHECKING THE FLIGHT STATUS AND UPDATING THE INFORMATION ON CLIENT SIDE WITH THE OPENED SOCKET
		'''
		self.__connectToMyNetwork__(connectionManager)
		start = time.time()
		self.vehicle.mode = VehicleMode('AUTO') #starting the mission
		self.fileTest.write("\nNumber of points: " + str(len(self.listOfLocationsToReach)) + "\n")
		self.fileTest.write("\nInitial Battery Level: " +  str(self.getBattery()) + "\n")
		eventlet.sleep(self.__generatingRandomSleepTime__())
		index = 0
		next = -1
		while True:
			s = time.time()
			self.__connectToMyNetwork__(connectionManager)
			#I'm getting next command from drone in flight
			if next != self.vehicle.commands.next:
				print "there are " + str(self.vehicle.commands.next - next) + " points I did not notify.."
				next = self.vehicle.commands.next
				if next%2!=0:
					next-=1
				while index <= (next/2):
					location = self.listOfLocationsToReach[index]
					#writing on the file
					#I would not write these information in the file, it's not important at this point.
					self.fileTest.write("Location:\n\t- latitude: " + str(location.lat))
					self.fileTest.write("\n\t- longitude: " +  str(location.lon))
					self.fileTest.write("\n\t- altitude: " + str(location.alt))
					self.fileTest.write("\n\t- battery: " + str(self.getBattery()))
					self.fileTest.write("\n\t- time: " + str(time.time()-start) + "\n")
					self.__connectToMyNetwork__(connectionManager)
					self.__sendFlightDataToClientUsingSocket__(socket, location, reached = True, RTLMode = False, typeOfSurvey = 'normal', numberOfOscillations = None)
					index+=1
					eventlet.sleep(self.__generatingRandomSleepTime__())
				#checking if drone has endend its trip
				if index == len(self.listOfLocationsToReach):
					print "Just finished to send all the live information via socket.." + self.name
					break
			eventlet.sleep(self.__generatingRandomSleepTime__())

		'''
		CLEARING ALL THE DATA STRUCTURES USED FOR THIS FLIGHTS
		'''
		#clear this for the
		end = time.time()
		self.__removeAllTheElementInTheListOfLocationsToReach__()
		self.__connectToMyNetwork__(connectionManager)
		#for the future: I need to delete this chaning mode part
		self.vehicle.mode = VehicleMode('GUIDED')
		self.vehicle.mode = VehicleMode('RTL')
		self.fileTest.write("\nFlight time: " + str(end-start))
		self.fileTest.write("\nFinal Battery level: " + str(self.getBattery()) + "\n")
		self.fileTest.write("\n###########################################\n")
		self.fileTest.close()
		self.__updateFileOldSurvey__()
		self.__sendFlightDataToClientUsingSocket__(socket, self.vehicle.location.global_frame, reached = False, RTLMode = True, typeOfSurvey = 'normal', numberOfOscillations = None)
		return True


	def newflightWithTheUsingOfSolosMemory(self, connectionManager, socket):

		print "Mission Flight for ", self.name
		self.fileTest = open("Riccardo test " + self.name + ".txt", "a")
		self.__connectToMyNetwork__(connectionManager)
		#writing on the file
		self.fileTest.write("Mission Flight starts on " +  str(time.strftime("%c")) + '\n')
		'''
		UPLOADING COMMANDS INTO THE SOLO'S MEMORY
		'''
		self.__uploadCommandsIntoSoloMemoryVersionTwo__()
		socket.emit('Take off ack', self.name + " has just taken off. Now it is ready to start the mission.")
		print "after cleaning, ready to go to sleep.. " + self.name

		eventlet.sleep(self.__generatingRandomSleepTime__())

		'''
		STARTING THE MISSION, CHECKING THE FLIGHT STATUS AND UPDATING THE INFORMATION ON CLIENT SIDE WITH THE OPENED SOCKET
		'''
		self.__connectToMyNetwork__(connectionManager)
		start = time.time()
		self.vehicle.mode = VehicleMode('AUTO') #starting the mission
		self.fileTest.write("\nNumber of points: " + str(len(self.listOfLocationsToReach)) + "\n")
		self.fileTest.write("\nInitial Battery Level: " +  str(self.getBattery()) + "\n")
		end = 0
		battery_end = -1
		eventlet.sleep(self.__generatingRandomSleepTime__())
		index = 0
		next = -1
		while True:
			self.__connectToMyNetwork__(connectionManager)
			#I'm getting next command from drone in flight
			if next != self.vehicle.commands.next:
				next = self.vehicle.commands.next
				#this happens when there is the last commands, so the RTL command
				if next == len(self.vehicle.commands)-1:
					next-=1
					end = time.time()
					battery_end = self.getBattery()
					print "Just finished to process all the commands, returning home"
				if next%2!=0:
					next-=1
				while index <= (next/2):
					location = self.listOfLocationsToReach[index]
					self.__connectToMyNetwork__(connectionManager)
					self.__sendFlightDataToClientUsingSocket__(socket, location, reached = True, RTLMode = False, typeOfSurvey = 'normal', numberOfOscillations = None)
					index+=1
					eventlet.sleep(self.__generatingRandomSleepTime__())
				#checking if drone has endend its trip
				if index == len(self.listOfLocationsToReach):
					print "Just finished to send all the live information via socket.." + self.name
					break
			eventlet.sleep(self.__generatingRandomSleepTime__())
		'''
		CLEARING ALL THE DATA STRUCTURES USED FOR THIS FLIGHTS
		'''
		#clear this for the
		self.__removeAllTheElementInTheListOfLocationsToReach__()
		#for the future: I need to delete this chaning mode part
		self.fileTest.write("\nFlight time: " + str(end-start))
		self.fileTest.write("\nFinal Battery level: " + str(battery_end) + "\n")
		self.fileTest.write("\n###########################################\n")
		self.fileTest.close()
		self.__updateFileOldSurvey__()
		self.__connectToMyNetwork__(connectionManager)
		self.__sendFlightDataToClientUsingSocket__(socket, self.vehicle.location.global_frame, reached = False, RTLMode = True, typeOfSurvey = 'normal', numberOfOscillations = None)
		return True

	'''
	This method is used for updating the file with the information about the old survey.
	The purpose of this method is for cheating the experiments.
	'''
	def __updateFileOldSurvey__(self):
		missionDivisionData = (open("oldSurvey.txt", "r").read())
		missionDivisionData = eval(missionDivisionData)
		for index in range(0, len(missionDivisionData['UAVs'])):
			if missionDivisionData['UAVs'][index]['name'] == self.name and missionDivisionData['UAVs'][index]['to complete'] == True:
				missionDivisionData['UAVs'][index]['to complete'] = False
				missionDivisionData['UAVs'][index]['completed'] = True
				file = open("oldSurvey.txt", "w")
				file.write(str(missionDivisionData))
				file.close()
				return

	'''
	This method uploads all the commands (waypoints and locations) into the Solo's memory.
	Moreover it writes on a file for the geotagging of each photo.
	The steps in this method are:
	1. preparing the commands to upload and writing the information about the geotagging
	2. taking off
	3. uploading the commands into the Solo's memory
	Uploading the commands after the taking off is done for preventing the "cutting the grass" effect.
	'''
	def __uploadCommandsIntoSoloMemory__(self):
		cmds = self.vehicle.commands
		#index for association between picture and location
		index = 0
		#open the file for the picture-location association
		pictures_file = open("association picture-location Solo " + self.name + ".txt", "a")
		pictures_file.write("Survey: " + str(time.strftime("%c")) + "\n")
		#adding waypoint and takeAPicture commands
		for location in self.listOfLocationsToReach:
			locationCommand = Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, location.lat, location.lon, location.alt)
			pictureCommand = Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_DO_DIGICAM_CONTROL, 0, 0, 1, 0, 0, 0, 1, 0, 0)
			pictures_file.write("Index " + str(index) + " ---> " + "lat: " + str(location.lat) + ", lon: " + str(location.lon) + ", alt: " + str(location.alt) + "\n")
			index = index + 1
			cmds.add(locationCommand)
			cmds.add(pictureCommand)
		pictures_file.write("\n###########################################\n\n")
		pictures_file.close()
		#adding command for returning home when the mission will be ended
		#RTLCommand = Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0, 0, 0, 0, 0, 0, 0, 0, 0)
		#cmds.add(RTLCommand)
		#taking off command
		self.__armAndTakeOff__()
		#uploading commands to UAV
		cmds.upload()
		self.vehicle.commands.next = 0 #reset mission set to first(0) waypoint


	'''
	This method allows the drone's flight with specifying the airspeed of the drone.
	The behavior of this method is the same of the "flightWithTheUsingOfSoloMemory()"
	'''
	def flightWithTheUsingOfSolosMemoryVersionTwo(self, connectionManager, socket):
		print "Mission Flight for ", self.name
		self.fileTest = open("Riccardo test " + self.name + ".txt", "a")
		self.__connectToMyNetwork__(connectionManager)
		'''
		UPLOADING COMMANDS INTO THE SOLO'S MEMORY
		'''
		#downloading and clearing the commands actually in the drone's memory
		print "Cleaning the commands"
		cmds = self.vehicle.commands
		cmds.download()
		cmds.wait_ready()
		cmds.clear()
		print "Commands cleaned.."
		#changing speed in the vehicle for better pictures. Airspeed = 5
		changeSpeedCommand = Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED, 0, 0, 0, 5, 0, 1, 0, 0, 0)
		cmds.add(changeSpeedCommand)
		#index for association between picture and location
		index = 0
		#open the file for the picture-location association
		pictures_file = open("association picture-location Solo " + self.name + ".txt", "a")
		pictures_file.write("Survey: " + str(time.strftime("%c")) + "\n")
		#adding waypoint and takeAPicture commands
		for location in self.listOfLocationsToReach:
			locationCommand = Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, location.lat, location.lon, location.alt)
			pictureCommand = Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_DO_DIGICAM_CONTROL, 0, 0, 1, 0, 0, 0, 1, 0, 0)
			pictures_file.write("Index " + str(index) + " ---> " + "lat: " + str(location.lat) + ", lon: " + str(location.lon) + ", alt: " + str(location.alt) + "\n")
			index = index + 1
			cmds.add(locationCommand)
			cmds.add(pictureCommand)
		pictures_file.close()
		self.fileTest.write("Number of points: " + str(len(self.listOfLocationsToReach)) + "\n")

		#adding return to launch command using mavlink protocol
		RTLCommand = Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0, 0, 0, 0, 0, 0, 0, 0, 0)
		cmds.add(RTLCommand)

		self.__armAndTakeOff__()
		#socket.emit('Take off ack', self.name + " has just taken off. Now it is ready to start the mission.")
		#uploading commands to UAV	def __uploadCommandsIntoSoloMemory__(self):
		cmds.upload()

		'''
		STARTING THE MISSION, CHECKING THE FLIGHT STATUS AND UPDATING THE INFORMATION ON CLIENT SIDE WITH THE OPENED SOCKET
		'''
		self.vehicle.commands.next = 0 #reset mission set to first(0) waypoint
		start = time.time()
		#starting the mission
		self.vehicle.mode = VehicleMode('AUTO')

		#writing on the file
		self.fileTest.write("Mission Flight starts on " +  str(time.strftime("%c")))
		self.fileTest.write("\nInitial Battery Level: " +  str(self.getBattery()) + "\n")
		eventlet.sleep(self.__generatingRandomSleepTime__())
		index = 0
		next = -1
		while True:
			self.__connectToMyNetwork__(connectionManager)
			#I'm getting next command from drone in flight
			if next != self.vehicle.commands.next and self.vehicle.commands.next != 0:
				print "there are " + str(self.vehicle.commands.next - next) + " points I did not notify.."
				next = self.vehicle.commands.next
				#checking if drone has endend its trip and so the next command is the RTL command
				if next%2==0:
					next-=1
				while index < (next/2):
					location = self.listOfLocationsToReach[index]
					#sending information via socket
					self.__connectToMyNetwork__(connectionManager)
					self.__sendFlightDataToClientUsingSocket__(socket, location, reached = True, RTLMode = False, typeOfSurvey = 'normal', numberOfOscillations = None)
					index+=1
					ss = time.time()
					eventlet.sleep(self.__generatingRandomSleepTime__())
					print "I have slept for " + str(time.time() - ss) + " for sending the next information via socket .. " + self.name
				if index == len(self.listOfLocationsToReach):
					print "Just finished to send all the live information via socket"
					break

			eventlet.sleep(self.__generatingRandomSleepTime__())

		'''
		CLEARING ALL THE DATA STRUCTURES USED FOR THIS FLIGHTS
		'''
		self.__removeAllTheElementInTheListOfLocationsToReach__()
		self.__connectToMyNetwork__(connectionManager)
		end = time.time()
		self.fileTest.write("\nFlight time: " + str(end-start))
		self.fileTest.write("\n###########################################\n\n")
		self.fileTest.close()
		self.__sendFlightDataToClientUsingSocket__(socket, self.vehicle.location.global_frame, reached = False, RTLMode = True, typeOfSurvey = 'normal', numberOfOscillations = None)
		return


	def __uploadCommandsIntoSoloMemoryVersionTwo__(self):
		cmds = self.vehicle.commands
		#index for association between picture and location
		index = 0
		#open the file for the picture-location association
		pictures_file = open("association picture-location Solo " + self.name + ".txt", "a")
		pictures_file.write("Survey: " + str(time.strftime("%c")) + "\n")
		#adding waypoint and takeAPicture commands
		for location in self.listOfLocationsToReach:
			locationCommand = Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, location.lat, location.lon, location.alt)
			pictureCommand = Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_DO_DIGICAM_CONTROL, 0, 0, 1, 0, 0, 0, 1, 0, 0)
			pictures_file.write("Index " + str(index) + " ---> " + "lat: " + str(location.lat) + ", lon: " + str(location.lon) + ", alt: " + str(location.alt) + "\n")
			index = index + 1
			cmds.add(locationCommand)
			cmds.add(pictureCommand)
		pictures_file.write("\n###########################################\n\n")
		pictures_file.close()
		#adding command for returning home when the mission will be ended
		RTLCommand = Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0, 0, 0, 0, 0, 0, 0, 0, 0)
		cmds.add(RTLCommand)
		#taking off command
		self.__armAndTakeOff__()
		#uploading commands to UAV
		cmds.upload()
		self.vehicle.commands.next = 0 #reset mission set to first(0) waypoint


	'''
	This method allows the flight with a 100% accuracy on live information on client side.
	The idea of this method is to send a flight command once a time. Only when the Solo reaches the location just processed, a new flight command will be sent.
	We can understand how far is the Solo from the location to reach and so decide if sending live information, taking the picture and at the end send the Solo to another location.
	This method is used inside the lab for testing purposes.
	'''
	def flightPointByPoint(self, connectionManager, socket):
		print "Inside flight method for ", self.name
		self.__connectToMyNetwork__(connectionManager)

		self.__armAndTakeOff__()
		socket.emit('Take off ack', self.name + " has just taken off. Now it is ready to start the mission.")
		print "Now " + self.name + " is going to sleep for a while.."
		eventlet.sleep(self.__generatingRandomSleepTime__())
		print "For " + self.name + " the number of locations to reach is ", len(self.listOfLocationsToReach)

		for location in self.listOfLocationsToReach:
			print "Location to reach this time: ", location
			self.__connectToMyNetwork__(connectionManager)
			droneCurrentLocation = self.vehicle.location.global_relative_frame
			distanceToNextLocation = self.__getDistanceFromTwoPointsInMeters__(droneCurrentLocation, location)
			print self.name + " is flying to ", location
			#self.vehicle.simple_goto(location)
			'''
			Now I have to check the location of the drone in flight, this because dronekit API is thought in order to have
			flight to single point and if I immediatelly send another location to reach, the drone will immediatelly change
			direction of its flight and it will go towards the new location I've just sent.
			'''
			while True:
				s = time.time()
				eventlet.sleep(self.__generatingRandomSleepTime__())
				print self.name + " is checking its location after a sleep of " + str(time.time() - s) + "\n"
				tolerance = 1
				self.__connectToMyNetwork__(connectionManager)
				currentDroneLocation = self.vehicle.location.global_relative_frame
				remainingDistanceToNextLocation = self.__getDistanceFromTwoPointsInMeters__(currentDroneLocation, location)
				#If I've just reached the location, I need to take a picture
				if remainingDistanceToNextLocation <= distanceToNextLocation*tolerance:
					print "Drone " + self.name + " has just reached the location and now it is taking a picture...\n"
					self.__takeAPicture__()
					self.__sendFlightDataToClientUsingSocket__(socket, location, reached = True, RTLMode = False, typeOfSurvey = 'normal', numberOfOscillations = None)
					break
				print self.name + "'s thread is going to sleep during the flight for awhile..\n"

		'''
		Now it's time to come back home
		'''
		self.__removeAllTheElementInTheListOfLocationsToReach__()
		self.__connectToMyNetwork__(connectionManager)
		print self.name + " has completed its mission and now it is coming back home."
		self.__sendFlightDataToClientUsingSocket__(socket, self.vehicle.location.global_frame, reached = False, RTLMode = True, typeOfSurvey = 'normal', numberOfOscillations = None)
		time.sleep(2)

	'''
	This method is used for flying continuously in two points until drone's battery reaches 20%.
	'''
	def oscillationFlight(self):
	  self.fileTest = open("test " + self.name + ".txt", "a")

	  cmds = self.__cleaningMissionsFromSoloMemory__()
	  if cmds is False:
		  return "Error on cleaning the Solo's memory"

	  for value in xrange(0, 500):
	    #even
	    if value%2 == 0:
	      locationCommand = Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, self.listOfLocationsToReach[0].lat, self.listOfLocationsToReach[0].lon, self.listOfLocationsToReach[0].alt)
	    #odd
	    else:
	      locationCommand = Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, self.listOfLocationsToReach[1].lat, self.listOfLocationsToReach[1].lon, self.listOfLocationsToReach[1].alt)
	    cmds.add(locationCommand)

	  cmds.upload() #sending commands to UAV

	  self.vehicle.commands.next = 0 #reset mission set to first(0) waypoint
	  self.__armAndTakeOff__()
	  start = time.time() #starting timer
	  self.vehicle.mode = VehicleMode('AUTO') #starting the mission
	  #writing on the file
	  self.fileTest.write("Mission Flight starts on " +  str(time.strftime("%c")))
	  self.fileTest.write("\nInitial Battery Level: " +  str(self.getBattery()) + "\n")
	  numberOfOscillations = 0
	  batteryLimit = 20
	  next = -1
	  while self.vehicle.battery.level >= batteryLimit:
	    if next != self.vehicle.commands.next:
	      next = self.vehicle.commands.next
	      #counting the number of oscillations
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

		if connectionManager.current() == self.wifiNetwork:
			print "already connected to " + self.wifiNetwork
			return False
		else:
			print "connecting to " + self.wifiNetwork + "..."
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
	This method deletes the elements in the array of locations to reach and so empty the array.
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

	'''
	This method uses a socket passed as parameter for sending live information to client about flight progresses.
	It uses the parameters for understanding if the Solo has endend its flight or it is still flying.
	'''
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

	'''
	This method builds the command required by MAVLink protocol for taking a picture and sends it to the Solo.
	'''
	def __takeAPicture__(self):
		msg = self.vehicle.message_factory.gopro_set_request_encode(1, 154, mavutil.mavlink.GOPRO_COMMAND_SHUTTER, (1, 0, 0, 0))
		self.vehicle.send_mavlink(msg)
		self.vehicle.commands.upload()

	'''
	This method checks the current network connection and returns True if the current network connection is the one generated by the
	current Solo, False otherwise.
	'''
	def __checkNetworkConnection__(self, connectionManager):
		if connectionManager.current() == self.wifiNetwork:
			return True
		else:
			return False

	def __cleaningMissionsFromSoloMemory__(self):
		try:
			print "Trying to clean the " + self.name + " memory."
			cmds = self.vehicle.commands
		  	cmds.download()
		  	cmds.wait_ready()
			print "Waiting for the download from the " + self.name +" memory..."
		  	time.sleep(30)
		  	cmds.clear()
			return True
		except Exception as e:
			print "Timeout expired. Error on cleaning the memory"
			return False
