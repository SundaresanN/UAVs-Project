from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit, send
import eventlet
import time
from serverbrain import ServerBrain

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/getDrones')
def getDrones():
	return jsonify(results=brain.dronesName)

@app.route('/connectDrone', methods=['POST'])
def connectDrone():
	data = request.get_json()
	message = brain.connectDrone(data["droneName"]) #this method returns a message if drone has been connected
	return  message 

@socketio.on('flight')
def flight(data):
	print "Creating thread for flight of, ", data['name']
	brain.activateThread("flight", data['name'], data['locationList'])

if __name__ == '__main__':
	
	brain = ServerBrain(socketio)
	app.debug = True
	socketio.run(app)