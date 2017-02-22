function addGraphicsInfoForTheRandomSurvey(){
  removingAllTheOldStuffs()
  $("#typeOfSurveyDiv").children().eq(0).children().eq(2).remove()
  for (element in brain.drones){
		checkbox = "<div class='row'>" +
									"<div class='col-lg-12'>" +
										"<div class='checkbox'>" +
												"<label><input type='checkbox'>" + brain.drones[element].name + "</label>" +
										"</div>" +
									"</div>" +
								"</div>"
		$("#typeOfSurveyDiv").children().eq(0).append(checkbox)
	}
  var buttons = "<div class='row'>" +
									"<div class='col-lg-12'>" +
										"<div class='row'>" +
											"<div class='col-lg-6'>" +
												"<p>" +
													"<a class='btn btn-success' id='randomSurveyButton'>Obtain Points</a>" +
												"</p>" +
											"</div>" +
											"<div class='col-lg-6'>" +
												"<p>" +
													"<a class='btn btn-danger' id='cancelRandomSurvey'>Cancel</a>" +
												"</p>" +
											"</div>" +
										"</div>" +
									"</div>" +
								"</div>"
	$("#typeOfSurveyDiv").children().eq(0).append(buttons)

  $("#randomSurveyButton").click(function(){
    var dronesSelected = new Array()
    var child = 2
    while($('#typeOfSurveyDiv').children().eq(0).children().eq(child).children().eq(0).children().hasClass('checkbox')){
      var drone = $('#typeOfSurveyDiv').children().eq(0).children().eq(child).children().eq(0).children().eq(0).children().eq(0).text()
      var index = brain.getIndexDrone(drone)
      if ($('#typeOfSurveyDiv').children().eq(0).children().eq(child).children().eq(0).children().eq(0).children().eq(0).children().eq(0).is(':checked')) {
        dronesSelected.push($('#typeOfSurveyDiv').children().eq(0).children().eq(child).children().eq(0).children().eq(0).children().eq(0).text())
      }
      child = child + 1
    }
    if (dronesSelected.length == 0) {
      alert("Please insert at least one drone for this type of survey.")
      return
    }
    if (dronesSelected.length == 2) {
      alert("This type of survey requests only one drone, so please select only one.")
      return
    }
    requestRandomPointsFromServer(dronesSelected[0])
  })

  $("#cancelRandomSurvey").click(function(){
    alert("Function to build")
  })
}

function requestRandomPointsFromServer(drone){
  $.ajax({
		type: 'POST',
		url: '/buildRandomPath',
		contentType: 'application/json',
    data: JSON.stringify({drone: drone}),
		success: function(data){
			data = data['data']
      if (data = 'ERROR') {
        alert("You need to be connected with " + drone + " in order to have a random survey. Retry!")
        return
      }
      var indexDrone = brain.getIndexDrone(data['drone'])
      // aggiungere parte per gestire l'inserimento dei punti sulla mappa
      for(var index in data['locations']){
        brain.drones[indexDrone].locationsToReach.push(new Location(data['locations'][index]['latitude'], data['locations'][index]['longitude'], data['locations'][index]['altitude']))
        addLocationForRandomSurveyInTheGUI(data['drone'], data['locations'][index])
      }
      // aggiungere parte per cambiare tipologia di bottone
      var flightRandomButton = "<div class='row'>" +
																			"<div class='col-lg-12'>" +
																				'<a type="button" class="btn btn-default" onclick="flightDrone(\'' +  data['drone'] + '\', \'' +  'normal' + '\')">Start Survey</a>' +
																			"</div>" +
																		"</div>"
			//Just need to understand what is the child for "build rectangular path" button and remove it.
      for (var i = 0; i < 3; i++) {
        $("#typeOfSurveyDiv").children().eq(0).children().eq(2).remove()
        }

			$("#typeOfSurveyDiv").children().eq(0).append(flightRandomButton)
		},
		error: function(){
			console.log("There is an error with obtaining points for the random survey on server side")
		}
	})
}

function addLocationForRandomSurveyInTheGUI(droneName, location){
	var xycoords = brain.converter.getXYCoordinatesFromLatitudeLongitudeCoordinates(location['latitude'], location['longitude'])
	brain.graphicBrain.addMarker(xycoords.x, xycoords.y, "location", droneName, brain.drones, 'normal', true)
	brain.graphicBrain.addLocationIntoTableOfLocationsToReach(droneName, brain.drones, location['latitude'], location['longitude'], location['altitude'], "location", "normal")

}
