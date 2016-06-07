function buildPath(droneName){


	var index = brain.getIndexDrone(droneName)
	if(brain.drones[index].locationsToReach.length == 0){
		alert("This drone has not locations to reach right now..")
		return
	}

	$.ajax({
		type: 'POST',
		url: '/buildPath',
		contentType: 'application/json',
		data: JSON.stringify({ droneName: droneName, locationsList: brain.drones[index].locationsToReach}),
		success: function(data){
			data = data['path']

			var element = brain.getIndexDrone(data['drone'])
			//adding the flight button in the dronesTable
			var flightButton = '<button type="button" class="btn btn-success" onclick="flightDrone(\'' +  brain.drones[element].name + '\')">Flight</button>'
			$("[id = '" + data['drone'] + "']").children().eq(3).html(flightButton)

		},
		error: function(){
			console.log("There is an error on server side")
		}
	})
	/*
	brain.socket.emit('build path', {name: droneName, locationsList: brain.drones[index].locationsToReach})

	brain.socket.on('path built', function(data){

		var element = brain.getIndexDrone(data['drone'])
		//adding the flight button in the dronesTable
		var flightButton = '<button type="button" class="btn btn-success" onclick="flightDrone(\'' +  brain.drones[element].name + '\')">Flight</button>'
		$("[id = '" + data['drone'] + "']").children().eq(3).html(flightButton)

	})
	*/
	/*
	brain.socket.on('Flight Informations Solo Gold', function(data){
		console.log('Solo Gold')
		var textToDisplay = "Drone " + data['name'] + "<br>" +
										"Drone location: " + "<br>" +
										" - latitude: " + data['location'][0] + "<br>" +
										" - longitude: " + data['location'][1] + "<br>" +
										" - altitude: " + data['location'][2] + "<br>"
		if (data['reached'] == true) {
			textToDisplay += "Reached location: " + data["reached"] + "<br>"
			//something to delete the location to the table
			updateGraphicAndDataStructureInformationsOnReachedLocation(data)
		}
		if (data['RTL'] == true) {
			textToDisplay = "Drone " + data['name'] + ' has completed its flight, now it is coming back home'
			//Now that the flight has been just completed, I need to reset the 'Build Path' button for having another flight
			var buildPathButton = '<button type="button" class="btn btn-success" onclick="buildPath(\'' +  brain.drones[element].name + '\')">Build Path</button>'
			$("[id = '" + droneName + "']").children().eq(3).html(buildPathButton)
		}
	  var divToDisplay = "<div class='well well-lg'>" + textToDisplay + "</div>"
		$("#liveFlightInformations").children().eq(1).prepend(divToDisplay)
	})
	*/
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
			$.ajax({
				type: 'POST',
				url: '/twoPointsFlight',
				contentType: 'application/json',
				data: JSON.stringify({ name: droneName }),
				success: function(data){
					console.log(data)
					/*
					var element = brain.getIndexDrone(data['drone'])
					//adding the flight button in the dronesTable
					var flightButton = '<button type="button" class="btn btn-success" onclick="flightDrone(\'' +  brain.drones[element].name + '\')">Flight</button>'
					$("[id = '" + data['drone'] + "']").children().eq(3).html(flightButton)
					*/
				},
				error: function(){
					console.log("There is an error on server side")
				}
			})

			/*
			brain.socket.emit('two points flight', {'name' : droneName}, function(){
					alert("Drone is flying with Two Points Flight..")
				})
			*/
			}
	} else {
		//This means that I have a "normal" flight to accomplish
		//brain.socket.emit('flight', {'name': droneName})
		$.ajax({
			type: 'POST',
			url: '/flight',
			contentType: 'application/json',
			data: JSON.stringify({ name: droneName }),
			success: function(data){
				console.log(data)
				/*
				var element = brain.getIndexDrone(data['drone'])
				//adding the flight button in the dronesTable
				var flightButton = '<button type="button" class="btn btn-success" onclick="flightDrone(\'' +  brain.drones[element].name + '\')">Flight</button>'
				$("[id = '" + data['drone'] + "']").children().eq(3).html(flightButton)
				*/
			},
			error: function(){
				console.log("There is an error on server side")
			}
		})
	}

	brain.socket.on('Flight Information', function(data){
		console.log("I'm here in Flight Information")
		var textToDisplay = "Drone " + data['name'] + "<br>" +
										"Drone location: " + "<br>" +
										" - latitude: " + data['location'][0] + "<br>" +
										" - longitude: " + data['location'][1] + "<br>" +
										" - altitude: " + data['location'][2] + "<br>"
		if (data['reached'] == true) {
			textToDisplay += "Reached location: " + data["reached"] + "<br>"
			//something to delete the location to the table
			updateGraphicAndDataStructureInformationsOnReachedLocation(data)
		}
		if (data['RTL'] == true) {
			textToDisplay = "Drone " + data['name'] + ' has completed its flight, now it is coming back home'
			//Now that the flight has been just completed, I need to reset the 'Build Path' button for having another flight
			var buildPathButton = '<button type="button" class="btn btn-success" onclick="buildPath(\'' +  drone['name'] + '\')">Build Path</button>'
			$("[id = '" + droneName + "']").children().eq(3).html(buildPathButton)
		}
		var divToDisplay = "<div class='well well-lg'>" + textToDisplay + "</div>"
		if($("#liveFlightInformation").children().eq(0).children().eq(0).children().eq(1).html() != textToDisplay) {
			$("[id = '" + droneName + "']").children().eq(2).html(data['battery'])
			$("#liveFlightInformation").children().eq(0).children().eq(0).children().eq(1).prepend(divToDisplay)
		}else{
			console.log("Second time same thing")
		}

	})
}

function updateGraphicAndDataStructureInformationsOnReachedLocation(data){

			for(var index=0; index<$("#locationsToReach > tbody > tr").length; index++){

				var latitude = $("#locationsToReach > tbody").children().eq(index).children().eq(2).html()
				var longitude = $("#locationsToReach > tbody").children().eq(index).children().eq(3).html()

				if (data["location"][0] == latitude && data["location"][1] == longitude) {
					// These following 3 lines of code are used to remove the marker of the location just reached from map
					var marker = $("#locationsToReach > tbody").children().eq(index).children().eq(1).html()
					var idMarker = data['name'] + (marker.charCodeAt()-96)
					$("[id = '" + idMarker + "']").remove()
					//this line of code is used for deleting the row which represents a location just reached
					$("#locationsToReach > tbody").children().eq(index).remove()
					var indexDrone = brain.getIndexDrone(data["name"])
					brain.drones[indexDrone].deleteElementWithLatitudeAndLongitude(latitude, longitude)
					index = $("#locationsToReach > tbody > tr").length
				}
		}
}
