//This is the only global variable and it will be an instance of ClientBrain class
var brain

$(document).ready(function(){

	var socketio = io.connect('http://' + document.domain + ':' + location.port)

	var map = new Map("MST Campus", 37.955879, -91.775020, 20, 640, 640, '/static/Images/Map\ Images/MSTStaticMap20zoom.png')

	brain = new ClientBrain(socketio, map)

	getDronesInfoFromServer()
})

function getDronesInfoFromServer(){

	//this function sends a request to server to obtain all the drones
	//available in the system and set the drones array in brain.drones
	$.ajax({
		type: 'GET',
		url: '/getDrones',
		contentType: 'application/json',
		success: function(drones){
			drones = drones['results']
			
			for(index in drones){
				
				brain.drones.push(new Drone(drones[index]))
			}
			
			brain.initialGraphicSettings()
			
		},
		error: function(){
			$('h1').remove()
			alert("Something went wrong.. check your wifi conncetion, you have to be connected with Solo WiFi")
		}
	})
}

//this function is called when user clicks on "Connect" button 
//in each row of drones table.
function connectDrone(droneName){
	
	console.log(droneName)

	$("[id ='" + droneName + "']").children().eq(1).html("Trying to connect...")
	
	
	$.ajax({
		type: 'POST',
		url: '/connectDrone',
		contentType: 'application/json',
		data: JSON.stringify({ droneName: droneName}),
		success: function(message){
			
			if (message == droneName + " netwotk is not reacheble") {
				alert(message)
				$("[id ='" + droneName + "']").children().eq(1).html("Not connected(previous error)")
			
			} else{
				
				var element = brain.getIndexDrone(droneName)
				var flightButton = '<button type="button" class="btn btn-success" onclick="flightDrone(\'' +  brain.drones[element].name + '\')">Flight</button>' 
	
				$("[id = '" + droneName + "']").children().eq(1).html("Connected")
				$("[id = '" + droneName + "']").children().eq(2).html(flightButton)

				var location = brain.converter.getXYCoordinatesFromLatitudeLongitudeCoordinates(parseFloat(message.latitude), parseFloat(message.longitude))
				brain.graphicBrain.addMarker(location.x, location.y, 'home', droneName) 
				brain.graphicBrain.addLocationIntoTableOfLocationsToReach(droneName, brain.drones, message.latitude, message.longitude, 0)
			}
		},
		error: function(){
			
			alert("Something went wrong.. check your wifi conncetion, you have to be connected with Solo WiFi")
		}
	})
}




