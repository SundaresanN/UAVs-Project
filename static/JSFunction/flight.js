function buildPath(droneName){


	var index = brain.getIndexDrone(droneName)
	if(brain.drones[index].locationsToReach.length == 0){
		alert("This drone has not locations to reach right now..")
		return
	}

	brain.socket.emit('build path', {name: droneName, locationsList: brain.drones[index].locationsToReach}, function(){
		console.log("Send data for building the path for ", droneName)
	})

	brain.socket.on('path built', function(data){

		console.log("Locations to reach for " + data['drone'] + ": " + data['locations to reach'])
		var element = brain.getIndexDrone(data['drone'])
		//adding the flight button in the dronesTable
		var flightButton = '<button type="button" class="btn btn-success" onclick="flightDrone(\'' +  brain.drones[element].name + '\')">Flight</button>'
		$("[id = '" + data['drone'] + "']").children().eq(3).html(flightButton)

	})

	brain.socket.on('Flight Informations', function(data){
		console.log("I'm here")
		console.log(data)
		if($('#liveFlightInformations').html()==undefined){
			var liveFlightInformations = "" +
				"<div id='liveFlightInformations' class='col-lg-6' style='width: 45%;>" +
							"<h3> Live Flight Informations</h3>" +
							"<div>" +
							"</div>" +
						"</div>"
			$("#secondRow").append(liveFlightInformations)
		}
		var textToDisplay = "Drone " + data['name'] + "<br>" +
										"Drone location: " + "<br>" +
										" - latitude: " + data['location'][0] + "<br>" +
										" - longitude: " + data['location'][1] + "<br>" +
										" - altitude: " + data['location'][2] + "<br>"
		if (data['reached'] == true) {
			textToDisplay += "Reached location: " + data["reached"] + "<br>"
			//something to delete the location to the table
			var index = brain.getIndexDrone(data['name'])
			var location = data['location'] //data['location'] is an array that cotains infos about the locations drone has to reach. First element is lat, second one is lon and third one is alt
			brain.drones[index].deleteElementWithLatitudeAndLongitude(location[0], location[1])
		}
		if (data['RTL'] == true) {
			textToDisplay = "Drone " + data['name'] + ' has completed its flight, now it is coming back home'
		}
	  var divToDisplay = "<div class='well well-lg'>" + textToDisplay + "</div>"
		$("#liveFlightInformations").children().eq(1).prepend(divToDisplay)
	})

}



function flightDrone(droneName){

	var index = brain.getIndexDrone(droneName)

	//I need to check if the two points flight is checked, and if it is I need to check if the drone has at least to points to reach
	if ($("[id = '" + droneName + "']").children().eq(6).children().eq(0).prop('checked') == true){

		if (brain.drones[index].locationsToReach.length < 2){
			alert(droneName + " cannot flight in 'two points flight' mode because this drone has not enough points(at least 2)")
			$("[id = '" + droneName + "']").children().eq(6).children().eq(0).prop('checked', false)
			return
		} else{
					brain.socket.emit('two points flight', {'name' : droneName}, function(){
					alert("Drone is flying with Two Points Flight..")
				})
			}
	} else {
		//This means that I have a "normal" flight to accomplish
		brain.socket.emit('flight', {'name': droneName}, function(){
			console.log("Drone is flying with Normal Flight...")
		})
	}

	//In this section you could add the code for updating the distance between drone and locations to reach
	/*
	brain.socket('Update distance', function(data){

	... something to do,,,
	... You have to decide where you can display this update ...
})
	*/
}
