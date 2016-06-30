/*
This function opens a socket for receiving live data to show for eache drone in flight mode
*/
function openSocket(droneName){
	brain.socket.on('Flight Information ' + droneName, function(data){
		console.log("receiving data from " + droneName + " for flight information")
		var textToDisplay = "Drone " + data['name'] + "<br>" +
										"Drone location: " + "<br>" +
										" - latitude: " + data['location'][0] + "<br>" +
										" - longitude: " + data['location'][1] + "<br>" +
										" - altitude: " + data['location'][2] + "<br>"
		if (data['reached'] == true) {
			textToDisplay += "Reached location: " + data["reached"] + "<br>"
			//something to delete the location to the table
			updateGraphicAndDataStructureInformationOnReachedLocation(data)
		}
		if (data['RTL'] == true) {
			//Now that the flight has been just completed, I need to reset the 'Build Path' button for having another flight
			var buildPathButton = '<button type="button" class="btn btn-success" onclick="buildPath(\'' +  droneName + '\')">Build Path</button>'
			textToDisplay = "Drone " + data['name'] + ' has completed its flight, now it is coming back home'
			$("[id = '" + droneName + "']").children().eq(3).html(buildPathButton)
		}
		var divToDisplay = "<div class='well well-lg'>" + textToDisplay + "</div>"
		if($("#liveFlightInformation").children().eq(0).children().eq(0).children().eq(1).children().eq(0).html() != textToDisplay) {
			$("[id = '" + droneName + "']").children().eq(2).html(data['battery'])
			$("#liveFlightInformation").children().eq(0).children().eq(0).children().eq(1).prepend(divToDisplay)
		}else{
			console.log("Second time same thing")
		}
	})
}
/*
This function is used for updating data structure of Drone class for a particular drone, whose name will be given as parameter
The update we are going to implement is the deleting of a location(given latitude and longitude) in the array of locations to reach, which is a member of the class Drone.
Moreover the marker on the map for the location to delete will be removed.
*/
function updateGraphicAndDataStructureInformationOnReachedLocation(data){

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


/*
This function is called when user confirms which survey do.
*/
function confirmedSurvey(){
	$("#tableInfo").remove()
	brain.graphicBrain.clickOnMap = false
	var typeOfSurvey = $("#selectTypeOfSurvey option:selected").text()
	switch (typeOfSurvey) {
		case 'Normal Survey':
			brain.typeOfSurvey = 'normal'
			break;
		case 'Rectangular Survey':
			//Setting up this data member of the ClientBrain instance, I set up the rectangular survey mode, so only the drones involved in
			// it can fly, the others must wait the end of the rectangular surbey flight.
			brain.typeOfSurvey = 'rectangular'
			addGraphicsInfoForTheRectangularSurvey()
			break;
		case 'Oscillation Survey':
			brain.typeOfSurvey = 'oscillation'
			addGraphicsInfoForTheOscillationSurvey()
			break;
			}
}
