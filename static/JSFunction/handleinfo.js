function addLocation(){
	if ($("#altitude").val() == 0) {
		alert("Fill the altitude field!")
		return
	}
	var location = new Location(parseFloat($("#latitude").val()), parseFloat($("#longitude").val()), parseFloat($("#altitude").val()))
	var xycoords = brain.converter.getXYCoordinatesFromLatitudeLongitudeCoordinates(location.latitude, location.longitude)
	var drone = '-'

	if (brain.typeOfSurvey == 'normal') {
		addingLocationForNormalSurvey(location, xycoords)
	}
	if (brain.typeOfSurvey == 'rectangular') {
		if(addingLocationForRectangularSurvey(location, xycoords) == -1){
			//This means that there are problems with the adding location for rectangular survey
			return
		}
	}
	if (brain.typeOfSurvey == 'oscillation') {
		if(addingLocationForOscillationSurvey(location, xycoords) == -1){
			//This means that there are problems with the adding location for oscillations survey
			return
		}
	}

	brain.graphicBrain.clickOnMap = false
	$("#tableInfo").remove()
}

function cancelAdding(){

	brain.graphicBrain.clickOnMap = false
	$("#tableInfo").remove()
}

function addingLocationForNormalSurvey(location, xycoords){
	var drone = $("#selectDrone").val()
	for(index in brain.drones){
		if(brain.drones[index].name == drone){
			brain.drones[index].locationsToReach.push(location)
			brain.graphicBrain.addMarker(xycoords.x, xycoords.y, "location", drone, brain.drones, 'normal')
			brain.graphicBrain.addLocationIntoTableOfLocationsToReach(drone, brain.drones, location.latitude, location.longitude, location.altitude, "location", "normal")
			break
		}
	}
}

function addingLocationForRectangularSurvey(location, xycoords){
	//Remember that you need only 3 points for the rectangular survey
	if(brain.rectangularSurveyLocations.length == 3){
		alert("You have already inserted three locations, now you need to build the path for the survey!")
		return -1
	}
	drone = "-"
	brain.rectangularSurveyLocations.push(location)
	brain.graphicBrain.addMarker(xycoords.x, xycoords.y, "location", drone, null, 'rectangular')
	brain.graphicBrain.addLocationIntoTableOfLocationsToReach(drone, brain.rectangularSurveyLocations, location.latitude, location.longitude, location.altitude, "location", "rectangular")

}

function addingLocationForOscillationSurvey(firstLocation, xycoordsFirst){
	//check the number of locations inserted for the drone involved in this kind of survey
	var index = -1
	for(element in brain.drones){
		if (brain.drones[element].surveyMode == 'oscillation') {
			index = element
			break
		}
	}
	if(index==-1){
		alert("There isn't drone in oscillation mode")
		return -1
	}
	if (brain.drones[index].locationsToReach > 0) {
		alert("You have just inserted the locations for this kind of survey.")
		return -1
	}

	//Now I have to check if the user has inserted north/east/down coordinates
	if($("#north").val() == 0 && $("#east").val() == 0 && $("#down").val() == 0){
		alert("Insert at least one of the field north, east, down")
		return -1
	}
	//It's time to convert the NED coordinates in location in lat/lon/alt coordinates
	var north = parseFloat($("#north").val())
	var east = parseFloat($("#east").val())
	var down = parseFloat($("#down").val())

	secondLocation = brain.converter.convertNEDCoordinatesInLatLonAltCoordinates(firstLocation, north, east, down)
	xycoordsSecond = brain.converter.getXYCoordinatesFromLatitudeLongitudeCoordinates(secondLocation.latitude, secondLocation.longitude)

	brain.drones[index].locationsToReach.push(firstLocation)
	brain.graphicBrain.addMarker(xycoordsFirst.x, xycoordsFirst.y, "location", brain.drones[index].name, brain.drones, 'oscillation')
	brain.graphicBrain.addLocationIntoTableOfLocationsToReach(brain.drones[index].name, brain.drones, firstLocation.latitude, firstLocation.longitude, firstLocation.altitude, "location", "oscillation")

	brain.drones[index].locationsToReach.push(secondLocation)
	brain.graphicBrain.addMarker(xycoordsSecond.x, xycoordsSecond.y, "location", brain.drones[index].name, brain.drones, 'oscillation')
	brain.graphicBrain.addLocationIntoTableOfLocationsToReach(brain.drones[index].name, brain.drones, secondLocation.latitude, secondLocation.longitude, secondLocation.altitude, "location", "oscillation")

}

/*
This function is called when user clicks on "delete" button, this button is in each row of the locations table.
 data is an array with the following information:
	- 0: name of the drone
	- 1: latitude
	- 2: longitude
*/
function deleteLocation(drone, lat, lon){

	//This first if with drone equal to '-' is for the rectangular path
	if (drone == '-') {
		//remove from brain.rectangularSurveyLocations
		console.log("Sono qua")
		brain.removeLocationsFromRectangularSurveyLocations(lat, lon)
	}else{
		//this means that I'm in a normal survey and so I have the drone name
		var indexDrone = brain.getIndexDrone(drone)
		if (indexDrone == -1) {
			console.log("not defined, -1");
		}else{
			brain.drones[indexDrone].deleteElementWithLatitudeAndLongitude(lat, lon)
		}
	}
	//Now it's time to remove the graphical data(marker and row from the table)
	for(var index=0; index<$("#locationsToReach > tbody > tr").length; index++){
		var latitude = $("#locationsToReach > tbody").children().eq(index).children().eq(2).html()
		var longitude = $("#locationsToReach > tbody").children().eq(index).children().eq(3).html()
		if (lat == parseFloat(latitude) && lon == parseFloat(longitude)) {
			// These following 3 lines of code are used to remove the marker of the location just reached from map
			var marker = $("#locationsToReach > tbody").children().eq(index).children().eq(1).html()
			var idMarker = drone + (marker.charCodeAt()-96)
			$("[id = '" + idMarker + "']").remove()
			//this line of code is used for deleting the row which represents a location just reached
			$("#locationsToReach > tbody").children().eq(index).remove()
			return
		}
	}
}
