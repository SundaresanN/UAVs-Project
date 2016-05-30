
function flightDrone(droneName){

	var index = brain.getIndexDrone(droneName)

	//I need to check if the two points flight is checked, and if it is I need to check if the drone has at least to points to reach
	if ($("[id = '" + droneName + "']").children().eq(6).children().eq(0).prop('checked') == true){

		if (brain.drones[index].locationsToReach.length < 2){
			alert(droneName + " cannot flight in 'two points flight' mode because this drone has not enough points(at least 2)")
			$("[id = '" + droneName + "']").children().eq(6).children().eq(0).prop('checked', false)
			return
		} else{
				alert("This type of flight is based on only two points flight, this means that only the first two locations will be reached from the drone")
				brain.socket.emit('two points flight', {'name' : droneName}, function(){
					alert("Drone is flying with Two Points Flight..")
				})
			}
	} else {
		//This means that I have a "normal" flight to accomplish
		brain.socket.emit('flight', {'name': droneName}, function(){
			alert("Drone is flying with Normal Flight...")
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

function buildPath(droneName){

	alert("I'm here")

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
		alert("Locations to reach for " + data['drone'] + ": " + data['locations to reach'])
		//adding the flight button in the dronesTable
		var flightButton = '<button type="button" class="btn btn-success" onclick="flightDrone(\'' +  brain.drones[element].name + '\')">Flight</button>'
		$("[id = '" + data['drone'] + "']").children().eq(3).html(flightButton)

	})

}
