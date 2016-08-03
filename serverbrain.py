from wireless import Wireless
from drone import Drone
from flask_socketio import SocketIO, emit, send
from flask import jsonify
import eventlet
import time
import threading


class ServerBrain:

	def __init__(self, socket = None):

		self.socket = socket
		#used to switch connection
		self.connectionManager = Wireless()

		#array of drone initializer
		self.drones = {
			'Solo Gold' : None,
			'Solo Green' : None
		}

	'''
	This method returns a list that contains the name of the drones in the system
	'''
	def getDroneNames(self):
		droneList = list()
		for drone in self.drones:
			droneList.append(drone)
		return droneList

	'''
	This method is used for connecting Drone object with real drone
	'''
	def connectDrone(self, droneName):
		'''
		Trying to find a free network for the drone
		'''

		interface, network = self.__getNetwork__(droneName, 'drone')
		if (interface, network) == (False, False):
			return droneName + " network is not reacheable"
		else:
			infosToReturn = {}
			self.drones[droneName] = Drone(droneName, interface, network)
			print self.drones[droneName]
			self.drones[droneName].connect()
			infosToReturn['drone status'] = "available"
			infosToReturn['home location'] = self.drones[droneName].getCurrentLocation()
			infosToReturn['drone battery'] = self.drones[droneName].getBattery()
			infosToReturn['camera status'] = 'available'
			return infosToReturn

	'''
	This method uses a scheduling algorithm for locations to reach for the drones.
	When the algorithm finishes its work, the locations to reach will be assigned to each drone.
	'''
	def buildPath(self, droneName, locationsToReach):
		'''
		algorithm for building a path for droneName
		'''
		self.drones[droneName].buildListOfLocations(locationsToReach)
		return {'drone': droneName, 'locations to reach' : self.drones[droneName].serializeListOfLocationsToReach()}

	'''
	This method generates the points inside the rectangular area delimited by the 3 points sent by client.
	If the 3 points are perfectly put from client, this method will return all the points to client and moreover it will assing these points to
	each drone involved in the survey on server side.
	'''
	def buildRectangularSurveyPointsReal(self, data):

		points = data['locationsList']
		altitude = points[0]['altitude']
		involvedDrones = data['drones']
		#check if involved drones are connected
		for drone in involvedDrones:
			if self.drones[drone] == None:
				missionDivisionData = {
					'response' : 'Connection Error',
					'body': 'You need to be connected with the drones involved in the rectangular survey'
				}
				return missionDivisionData
		pointsNewFormat = []
		import rectPlan
		for point in points:
			pointsNewFormat.append(rectPlan.latlon(point['latitude'], point['longitude']))

		result = rectPlan.rectMission(pointsNewFormat[0], pointsNewFormat[1], pointsNewFormat[2], altitude)
		if result == 'Bad':
			return result
		#print "Result: ", result['picList']

		droneList = []
		for drone in data['drones']:
			droneList.append(drone)
			location = self.drones[drone].getCurrentLocation()
			droneList.append(location['latitude'])
			droneList.append(location['longitude'])

		missionDivisionData = rectPlan.missionDivision(result, droneList)
		missionDivisionData = rectPlan.serializeMissionData(missionDivisionData)
		'''
		Assign locations to reach to each involved drone
		'''
		if missionDivisionData['response'] == 'Good' or missionDivisionData['response'] == 'Warn':
			#filling the locations to reach array for each drone involved
			for UAVInfo in missionDivisionData['UAVs']:
				drone = UAVInfo['name']
				self.drones[drone].buildListOfLocations(UAVInfo['points'])
		return missionDivisionData

	'''
	Same of precedent method but cheating...
	'''
	def buildRectangularSurveyPointsCheating(self, data):
		points = data['locationsList']
		altitude = points[0]['altitude']
		involvedDrones = data['drones']
		#check if involved drones are connected
		for drone in involvedDrones:
			if self.drones[drone] == None:
				missionDivisionData = {
					'response' : 'Connection Error',
					'body': 'You need to be connected with the drones involved in the rectangular survey'
				}
				return missionDivisionData
		pointsNewFormat = []
		import rectPlan
		for point in points:
			pointsNewFormat.append(rectPlan.latlon(point['latitude'], point['longitude']))

		result = rectPlan.rectMission(pointsNewFormat[0], pointsNewFormat[1], pointsNewFormat[2], altitude)
		if result == 'Bad':
			return result
		#print "Result: ", result['picList']

		droneList = []
		for drone in data['drones']:
			droneList.append(drone)
			location = self.drones[drone].getCurrentLocation()
			droneList.append(location['latitude'])
			droneList.append(location['longitude'])

		missionDivisionData = rectPlan.missionDivisionCheating(result, droneList, data['total'])
		#missionDivisionData = rectPlan.missionDivision(result, droneList)
		missionDivisionData = rectPlan.serializeMissionData(missionDivisionData)
		#dataToReturn is required for keeping data on missionDivisionData correct. In fact with the modify of "completed" field in eache UAVInfo object,
		#the risk is that client could not understand which points to show. File will be modified with the missionDivisionData updated for each drone("completed" key's value).
		dataToReturn = missionDivisionData
		'''
		Assign locations to reach to each involved drone
		'''
		if missionDivisionData['response'] == 'Good' or missionDivisionData['response'] == 'Warn':
			#filling the locations to reach array for each drone involved
			UAVInfo = missionDivisionData['UAVs']
			for index in xrange(0, len(UAVInfo)):
				drone = UAVInfo[index]['name']
				#if drone has already a filled list of locations to reach, I need to go ahead
				#otherwise I need to understand if the mission has been already completed and if not I can assign points to the associated drone and set the key "completed" to True
				if self.drones[drone] is not None:
					if self.drones[drone].listOfLocationsToReach is None:
						self.drones[drone].buildListOfLocations(UAVInfo[index]['points'])
						UAVInfo[index]['to complete'] = True
				else:
					print "This drone has already locations to reach"
			missionDivisionData['UAVs'] = UAVInfo
			file = open("oldSurvey.txt", "w")
			file.write(str(missionDivisionData))
			file.close()
		return dataToReturn

	'''
	Used for cheating..
	'''
	def checkOldSurvey(self):
		#taking information about old survey not completed
		missionDivisionData = (open("oldSurvey.txt", "r").read())
		if len(missionDivisionData) == 0:
			return "No old survey to end"
		missionDivisionData = eval(missionDivisionData)
		#dataToReturt is required for keeping data on missionDivisionData correct. In fact with the modify of "completed" field in eache UAVInfo object,
		#the risk is that client could not understand which points to show. File will be modified with the missionDivisionData updated for each drone("completed" key's value).
		dataToReturn = missionDivisionData
		UAVInfo = missionDivisionData['UAVs']
		for index in xrange(0, len(UAVInfo)):
			drone = UAVInfo[index]['name']
			#if drone has already a filled list of locations to reach, I need to go ahead
			#otherwise I need to understand if the mission has been already completed and if not I can assign points to the associated drone and set the key "completed" to True
			if self.drones[drone] is not None:
				if self.drones[drone].listOfLocationsToReach is not None:
					print drone + " has already locations to reach"
				else:
					print drone + " has an empty list of locations"
					if UAVInfo[index]['completed'] == False:
						self.drones[drone].buildListOfLocations(UAVInfo[index]['points'])
						UAVInfo[index]['to complete'] = True
					else:
						print "This set of points has been completed"
		missionDivisionData['UAVs'] = UAVInfo
		file = open("oldSurvey.txt", "w")
		file.write(str(missionDivisionData))
		file.close()
		return dataToReturn

	'''
	This method creates a thread for a drone's flight.
	'''
	def takeAFlight(self, drone):
		eventlet.spawn(self.drones[drone].missionFlight, self.connectionManager, self.socket)


	'''
	This method allows the drone to have an oscillation flight.
	'''
	def takeAnOscillationFlight(self, drone):
		data = self.drones[drone].missionOscillationFlight()
		return data

	'''
	This method starts the rectangular survey flight.
	'''
	def takeARectangularFlight(self):
		for drone in self.drones:
			if self.drones[drone] is not None:
				if len(self.drones[drone].listOfLocationsToReach)>0:
					eventlet.spawn(self.drones[drone].missionFlight, self.connectionManager, self.socket)
					time.sleep(5)


	'''
	This method is used for building the network the drone will connect to.
	This method is private because it's usage is thought for this class and not for other classes.
	'''
	def __getNetworkName__(self, type, drone):
		color = drone.split()[1] # I've just taken the drone color from drone name(ex:'Solo Gold')
		if type == "drone":
			print "Drone setting network"
			wifiNetwork = "SoloLink_" + color + "Drone"
		return wifiNetwork

	'''
	This method has been designed for getting network interface value and wifi network name
	for the drone or for the camera.
	This method is private because its functions are thought for inside the class.
	'''
	def __getNetwork__(self, drone, type):
		wifiNetwork = self.__getNetworkName__(type, drone)
		print wifiNetwork
		'''This for-loop checks if this network is already connected '''
		for interface in self.connectionManager.interfaces():
			self.connectionManager.interface(interface)
			print self.connectionManager.current()
			if self.connectionManager.current() == wifiNetwork:
				print "You are already connected to this network, ", wifiNetwork
				self.connectionManager.connect(ssid = wifiNetwork, password = "Silvestri")
				return self.connectionManager.interface(), self.connectionManager.current()
			print self.connectionManager.current()
		'''This for-loop checks if this network has not a connection yet '''
		for interface in self.connectionManager.interfaces():
			self.connectionManager.interface(interface)
			if self.connectionManager.current() == None:
				print "I've just found one free antenna ready to be connected"
				if self.connectionManager.connect(ssid = wifiNetwork, password = "Silvestri"):
					return self.connectionManager.interface(), self.connectionManager.current()
				else:
					'''This could be possible if the network is not available '''
					return False, False

		print "I haven't found a free antenna for your connection... sorry, ", wifiNetwork
		return False, False
