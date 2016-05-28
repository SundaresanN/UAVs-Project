function addLocation(){

	if ($("#altitude").val() == 0) {

		alert("Fill the altitude field!")
		return
	}

	var location = new Location(parseFloat($("#latitude").val()), parseFloat($("#longitude").val()), parseFloat($("#altitude").val()))

	var drone = $("#selectDrone").val()


	brain.graphicBrain.clickOnMap = false

	$("#tableInfo").remove()

	for(index in brain.drones){

		if(brain.drones[index].name == drone){

			brain.drones[index].locationsToReach.push(location)
			xycoords = brain.converter.getXYCoordinatesFromLatitudeLongitudeCoordinates(location.latitude, location.longitude)
			console.log('adding a location marker ')
			brain.graphicBrain.addMarker(xycoords.x, xycoords.y, "location", drone, brain.drones)
			brain.graphicBrain.addLocationIntoTableOfLocationsToReach(drone, brain.drones, location.latitude, location.longitude, location.altitude, "location")
			return
		}
	}

}

function cancelAdding(){

	brain.graphicBrain.clickOnMap = false
	$("#tableInfo").remove()
}
