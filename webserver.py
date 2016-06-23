from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit, send
import eventlet
import time
from serverbrain import ServerBrain
import socket

# Allow us to reuse sockets after the are bound.
# http://stackoverflow.com/questions/25535975/release-python-flask-port-when-script-is-terminated


app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/getDrones')
def getDrones():
	return jsonify(results=brain.getDroneNames())


@app.route('/connectDrone', methods=['POST'])
def connectDrone():
    data = request.get_json()
    message = brain.connectDrone(data['droneName'])
    return jsonify({'data' : message})

@app.route('/flight', methods=['POST'])
def flight():
    print "Inside flight"
    data = request.get_json()
    brain.takeAFlight(data['name'])
    return 'Flight started'

@app.route('/oscillationFlight', methods=['POST'])
def oscillationFlight():
    print "Inside oscillation flight"
    data = request.get_json()
    rData = brain.takeAnOscillationFlight(data['name'])
    return jsonify({'data' : rData})

@app.route('/twoPointsFlight', methods=['POST'])
def twoPointsFlight(data):
    print "Two points flight for ", data['name']
    brain.takeATwoPointsFlight(data['name'])
    return 'Two Points Flight Completed'

@app.route('/buildPath', methods=['POST'])
def buildPath():
    data = request.get_json()
    print data
    path = brain.buildPath(data['droneName'], data['locationsList'])
    return jsonify({'path' : path})

if __name__ == '__main__':
    brain = ServerBrain(socketio)
    app.debug = True
    app.threaded = True
    socketio.run(app)
