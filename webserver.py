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

@app.route('/checkOldSurvey', methods=['GET'])
def checkOldSurvey():
    return jsonify({'data': brain.checkOldSurvey()})

@app.route('/connectDrone', methods=['POST'])
def connectDrone():
    data = request.get_json()
    message = brain.connectDrone(data['droneName'])
    return jsonify({'data' : message})

@app.route('/buildPath', methods=['POST'])
def buildPath():
    data = request.get_json()
    path = brain.buildPath(data['droneName'], data['locationsList'])
    return jsonify({'path' : path})

@app.route('/buildRectangularPath', methods=['POST'])
def buildRectangularPath():
    data = request.get_json()
    dataToReturn = brain.buildRectangularSurveyPointsCheating(data)
    return jsonify({'data' : dataToReturn})

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

@app.route('/rectangularFlight', methods=['POST'])
def rectangularFlight():
    print "Inside rectangular flight"
    brain.takeARectangularFlight()
    return "rectangular flight launched"

@app.route('/twoPointsFlight', methods=['POST'])
def twoPointsFlight(data):
    print "Two points flight for ", data['name']
    brain.takeATwoPointsFlight(data['name'])
    return 'Two Points Flight Completed'

@socketio.on('response for live information')
def receive_live_info(message):

    print "##########################################"
    print "Just received the ack from client for arrived live information.."
    print "Message says: " + message
    print "##########################################"
    print "\n"

@socketio.on('refreshing')
def refreshing():
    print "stopping the server.."
    

if __name__ == '__main__':
    print "Running the server..."
    brain = ServerBrain(socketio)
    app.threaded = True
    socketio.run(app, use_reloader=True, debug=True)
