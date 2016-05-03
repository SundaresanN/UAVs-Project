from dronekit import connect, VehicleMode, LocationGlobal, LocationGlobalRelative
from flask import jsonify

class Drone:

	def __init__(self, name, wifiConnection):

		self.targetAltitude = 2

		self.name = name
		
		self.vehicle = None
		
		self.listOfLocations = []
		
		self.wifiConnection = wifiConnection

		self.thread = {}

	def connect(self):
		self.vehicle = connect('udpout:10.1.1.10:14560', wait_ready=True)
		self.vehicle.airspeed = 1
		
	def getActualLocation(self):
		location = self.vehicle.location.global_frame
		location = {
			"latitude" : location.lat,
			"longitude" : location.lon, 
			"altitude" : self.vehicle.location.global_relative_frame.alt,
		}
		return jsonify(location)

	def buildListOfLocations(self, listOfLocations):

		for location in listOfLocations:
			if location != None:
				self.listOfLocations.append(LocationGlobalRelative(location["latitude"], location["longitude"], location['altitude']))
