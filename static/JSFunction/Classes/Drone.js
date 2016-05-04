function Drone(name){

	this.name = name

	this.homeLocation = null

	this.locationsToReach = new Array()

	this.flight = flight

	this.deleteElementWithLatitudeAndLongitude = deleteElementWithLatitudeAndLongitude
}


function flight(socket){

	if (this.locationsToReach.length == 0) {

		alert("You haven't inserted locations to reach for " + this.name + " drone yet.")

		return
	}

	$("[id = '" + this.name + "']").children().eq(2).html("-")
	
	socket.emit('flight', {name: this.name, locationList: this.locationsToReach}, function(){

		console.log("qua")
	})


}

function deleteElementWithLatitudeAndLongitude(latitude, longitude){

	for(index in this.locationsToReach){

		if (this.locationsToReach[index].latitude == latitude && this.locationsToReach[index].longitude == longitude) {

			this.locationsToReach.splice(index, 1)
		}
	}
}