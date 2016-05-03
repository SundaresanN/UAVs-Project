function Drone(name){

	this.name = name

	this.homeLocation = null

	this.locationsToReach = new Array()

	this.flight = flight
}


function flight(socket){

	if (this.locationsToReach.length == 0) {

		alert("You haven't inserted locations to reach for " + this.name + " drone yet.")

		return
	}

	$("[id = '" + this.name + "']").children().eq(2).html("-")
	
	socket.emit('flight', {name: this.name, locationList: this.locationsToReach})


	socket.on('Altitude Reached', function(data){

		var name = data['name']
		var altitude =  data['altitude']

		if (data['reached'] == true) {

			alert(name + " has reached its altitude, it is ready to flight")
		}else{

			console.log(name + " --> altitude reached: " + altitude)
		}

	})

	socket.on('Update Live Location', function(data){
		
		console.log(data)
		/*
		var xy = brain.converter.getXYCoordinatesFromLatitudeLongitudeCoordinates(data["latitude"], data["longitude"])
		var id = data["name"] + " " + "drone"

		if($("[id='" + id + "']").html() == null){
			brain.graphicBrain.addMarker(xy.x, xy.y, "drone", data["name"], null)
		}else{
			$("[id='" + id + "']").css({top: xy.y, left: xy.x})
		}
		*/
	})


}