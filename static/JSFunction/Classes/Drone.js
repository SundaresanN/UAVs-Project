function Drone(name){

	this.name = name

	this.homeLocation = null

	this.locationsToReach = new Array()

	this.deleteElementWithLatitudeAndLongitude = deleteElementWithLatitudeAndLongitude
}

function deleteElementWithLatitudeAndLongitude(latitude, longitude){

	for(index in this.locationsToReach){

		if (this.locationsToReach[index].latitude == latitude && this.locationsToReach[index].longitude == longitude) {

			this.locationsToReach.splice(index, 1)
		}
	}
}
