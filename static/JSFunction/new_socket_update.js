function openSocketNewVersion(drone_name){
  console.log(drone_name + " is opening a socket..")
  brain.socket.on('Flight live information ' + drone_name, function(data){
    console.log("Received something..")
    console.log(data);
    if (data['completed']==true) {
      console.log("Last message");
      //Now that the flight has been just completed, I need to reset the 'Build Path' button for having another flight
			var prepareSurveyButton = '<button type="button" class="btn btn-success" onclick="buildPath(\'' +  drone_name + '\')">Prepare Survey</button>'
			$("[id = '" + drone_name + "']").children().eq(3).html(prepareSurveyButton)
      $("[id = '" + drone_name + "']").children().eq(2).html(data['battery'])
      var textToDisplay = "Drone " + drone_name + ' has completed its flight, now it is coming back home. The flight took ' + data['flight time'] + '.'
      var divToDisplay = "<div class='well well-lg'>" + textToDisplay + "</div>"
      $("#liveFlightInformation").children().eq(0).children().eq(0).children().eq(1).prepend(divToDisplay)
      return
    }
    if (data['last'] != -1) {
      updateDataAndUIDuringAFlight(drone_name, data['last'])
    }

  })
}

function updateDataAndUIDuringAFlight(drone_name, lastLoc){
  var indexDrone = brain.getIndexDrone(drone_name)
  for (var i = 0; i <= lastLoc; i++) {
    var lat = brain.drones[indexDrone].locationsToReach[i].latitude
    var lon = brain.drones[indexDrone].locationsToReach[i].longitude
    //removing marker on the map and row from the table of locations
    updateUIOnReachedLocation(drone_name, lat, lon, i)
  }
}

/*
This function is used for updating data structure of Drone class for a particular drone, whose name will be given as parameter
The update we are going to implement is the deleting of a location(given latitude and longitude) in the UI. Moreover live information associated with that location
will be showed in the specific section
*/
function updateUIOnReachedLocation(drone_name, lat, lon, locationIndex){

			for(var index=0; index<$("#locationsToReach > tbody > tr").length; index++){

				var latitude = $("#locationsToReach > tbody").children().eq(index).children().eq(2).html()
				var longitude = $("#locationsToReach > tbody").children().eq(index).children().eq(3).html()

				if (lat == latitude && lon == longitude) {
          console.log("Got " + locationIndex)
					// These following 3 lines of code are used to remove the marker of the location just reached from map
					var marker = $("#locationsToReach > tbody").children().eq(index).children().eq(1).html()
					var idMarker = drone_name + marker
					$("[id = '" + idMarker + "']").remove()
					//this line of code is used for deleting the row which represents a location just reached
					$("#locationsToReach > tbody").children().eq(index).remove()
					var indexDrone = brain.getIndexDrone(drone_name)
					//brain.drones[indexDrone].deleteElementWithLatitudeAndLongitude(latitude, longitude)
					index = $("#locationsToReach > tbody > tr").length
          //add post on the live information table
          updateLiveInformation(drone_name, lat, lon, locationIndex)
				}else{
          console.log(locationIndex + " has been already processed")
        }
		}
}

function updateLiveInformation(drone_name, latitude, longitude, index){
  var textToDisplay = "Drone " + drone_name + "<br>" +
                      "Drone location: " + "<br>" +
                      " - latitude: " + latitude + "<br>" +
                      " - longitude: " + longitude + "<br>" +
                      " - number: " + index+1 + "<br>"
  var divToDisplay = "<div class='well well-lg'>" + textToDisplay + "</div>"
  $("#liveFlightInformation").children().eq(0).children().eq(0).children().eq(1).prepend(divToDisplay)
}
