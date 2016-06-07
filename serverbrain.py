from wireless import Wireless
from drone import Drone
from camera import Camera
from flask_socketio import SocketIO, emit, send
from flask import jsonify
import eventlet
import time


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


	def connectDrone(self, droneName):
		'''
		Trying to find a free network for the drone
		'''
		print self.connectionManager.interfaces()
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

			'''now it's the camera time '''
			interface, network = self.__getNetwork__(droneName, 'camera')
			if (interface, network) == (False, False):
				print "Camera is not available for ", droneName
				self.drones[droneName].camera = None
				infosToReturn['camera status'] = 'not available'
				infosToReturn['camera battery'] = 'info not reacheable'
			else:
				print "Camera is available ", droneName
				self.drones[droneName].camera = Camera(interface, network, droneName)
				infosToReturn['camera status'] = 'available'
				infosToReturn['camera battery'] = '-'

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
	This method creates a thread for a drone's flight.
	'''
	def takeAFlight(self, drone):
		eventlet.spawn(self.drones[drone].flight, self.connectionManager, self.socket)
		#self.drones[drone].flight(self.connectionManager, self.socket)
	'''
	This method doesn't create a thread for the following kind of flight. We need to talk about
	priority this method could have.
	Max priority means that this kind of flight could not be interrupted by anything(so it's a process that requires all the power of the server)
	'''
	def takeATwoPointsFlight(self, drone):
		self.drones[drone].twoPointsFlight(self.connectionManager, self.socket)
	'''
	This method is used for building the network the drone will connect to.
	This method is private because it's usage is thought for this class and not for other classes.
	'''
	def __getNetworkName__(self, type, drone):
		color = drone.split()[1] # I've just taken the drone color from drone name(ex:'Solo Gold')
		if type == "drone":
			print "Drone setting network"
			wifiNetwork = "SoloLink_" + color + "Drone"
		if type == "camera":
			print "Camera setting network"
			wifiNetwork = "Solo" + color + "CameraRGB"
		return wifiNetwork

	'''
	This method has been designed for getting network interface value and wifi network name
	for the drone or for the camera.
	This method is private because its functions are thought for inside the class.
	'''
	def __getNetwork__(self, drone, type):
		wifiNetwork = self.__getNetworkName__(type, drone)

		'''This for-loop checks if this network is already connected '''
		for interface in self.connectionManager.interfaces():
			self.connectionManager.interface(interface)
			if self.connectionManager.current() == wifiNetwork:
				print "You are already connected to this network, ", wifiNetwork
				self.connectionManager.connect(ssid = wifiNetwork, password = "Silvestri")
				return self.connectionManager.interface(), self.connectionManager.current()

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
