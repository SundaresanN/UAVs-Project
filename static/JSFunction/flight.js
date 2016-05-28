function flightDrone(droneName){

	var index = brain.getIndexDrone(droneName)

	brain.drones[index].flight(brain.socket)

	brain.socket.on('Altitude Reached', function(data){

		var name = data['name']
		var altitude =  data['altitude']
		console.log(data)
		/*
		if (data['reached'] == true) {

			alert(name + " has reached its altitude, it is ready to flight")
		}else{

			console.log(name + " --> altitude reached: " + altitude)
		}
		*/



	})

	brain.socket.on('Update Live Location', function(data){

		//console.log(data)
		/*
		var xy = brain.converter.getXYCoordinatesFromLatitudeLongitudeCoordinates(data["latitude"], data["longitude"])
		var id = data["name"] + " " + "drone"

		if($("[id='" + id + "']").html() == null){
			brain.graphicBrain.addMarker(xy.x, xy.y, "drone", data["name"], null)
		}else{
			$("[id='" + id + "']").css({top: xy.y, left: xy.x})
		}
		*/
		console.log("dentro Update Live Location, " + data['name'])
		console.log(data)
		if(data["status"] == "reached"){

			for(var index=0; index<$("#locationsToReach > tbody > tr").length; index++){

				var latitude = $("#locationsToReach > tbody").children().eq(index).children().eq(2).html()
				var longitude = $("#locationsToReach > tbody").children().eq(index).children().eq(3).html()

				if (data["latitude"] == latitude && data["longitude"] == longitude) {

					$("#locationsToReach > tbody").children().eq(index).remove()
					var indexDrone = brain.getIndexDrone(data["name"])
					console.log("Ho eliminato la " + indexDrone + " location")
					brain.drones[indexDrone].deleteElementWithLatitudeAndLongitude(latitude, longitude)
					index = $("#locationsToReach > tbody > tr").length
				}
			}
		}
	})
}

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
		alert("Locations to reach for " + data['drone'] + ": " + data['locations to reach'])

		var flightButton = '<button type="button" class="btn btn-success" onclick="flight(\'' +  brain.drones[element].name + '\')">Flight</button>'
		$("[id = '" + data['drone'] + "']").children().eq(3).html(flightButton)

	})
}
