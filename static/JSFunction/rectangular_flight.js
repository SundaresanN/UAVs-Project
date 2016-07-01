function addGraphicsInfoForTheRectangularSurvey(){
		removingAllTheOldStuffs()
		$("#typeOfSurveyDiv").children().eq(0).children().eq(2).remove()
		var checkbox = ''
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
											"<button type='button' class='btn btn-primary' id='confirmRectangularSurvey'>Confirm</button>" +
											"<button type='button' class='btn btn-danger' id='cancelSurvey'>Cancel</button>" +
										"</div>" +
									"</div>"
		$("#typeOfSurveyDiv").children().eq(0).append(buttons)

		$("#cancelSurvey").click(function(){
				deleteDataOfRectangularSurvey()
				while($('#typeOfSurveyDiv').children().eq(0).children().eq(2).html() != undefined){
					$('#typeOfSurveyDiv').children().eq(0).children().eq(2).remove()
				}
				var button = "<div class='row'>" +
												"<div class='col-lg-12'>" +
													"<button type='button' class='btn btn-primary' id='confirmedSurvey' onclick='confirmedSurvey()'>Confirm</button>" +
												"</div>" +
											"</div>"
				$("#typeOfSurveyDiv").children().eq(0).append(button)
		})

		$("#confirmRectangularSurvey").click(function(){

			var dronesSelected = new Array()
			var child = 2
			while($('#typeOfSurveyDiv').children().eq(0).children().eq(child).children().eq(0).children().hasClass('checkbox')){
				var drone = $('#typeOfSurveyDiv').children().eq(0).children().eq(child).children().eq(0).children().eq(0).children().eq(0).text()
				var index = brain.getIndexDrone(drone)
				if ($('#typeOfSurveyDiv').children().eq(0).children().eq(child).children().eq(0).children().eq(0).children().eq(0).children().eq(0).is(':checked')) {
					console.log("adding drone..");
					dronesSelected.push($('#typeOfSurveyDiv').children().eq(0).children().eq(child).children().eq(0).children().eq(0).children().eq(0).text())
				}
				child = child + 1
			}
			if (dronesSelected.length == 0) {
				alert("Please insert at least one drone for this type of survey.")
				return
			}
			console.log(dronesSelected)
			prepareRectangularSurvey(dronesSelected)
		})
}

//This function will remove the graphic components in the drones table and will replace them with the components correllated with the
//retangular survey
function prepareRectangularSurvey(drones){
	//Deleting the 'build path' buttons, if present, on the drones table and replacing them with the string 'rectangular survey mode'
	for(element in drones){
		var index = brain.getIndexDrone(drones[element])
		brain.drones[index].surveyMode = "rectangular"
		if($("[id = '" + drones[element] + "']").children().eq(3).children().eq(0).text() == 'Build Path'){
			$("[id = '" + drones[element] + "']").children().eq(3).html('Rectangular Survey Mode')
		}
	}
	//Adding button for building the rectangular path
	var index = 0
	while($("#typeOfSurveyDiv").children().eq(0).children().eq(index).html() != undefined){
		if ($("#typeOfSurveyDiv").children().eq(0).children().eq(index).text() == "Build Rectangular Path") {
			return
		}
		index++
	}
	var buildRectangularPathButton = "<div class='row'>" +
													"<div class='col-lg-12'>" +
														'<button type="button" class="btn btn-success" onclick="buildRectangularPath()">Build Rectangular Path</button>' +
													"</div>" +
												"</div>"

	$("#typeOfSurveyDiv").children().eq(0).append(buildRectangularPathButton)
}

/*
This function sends the AJAX request to server for obtaining the list of points inside the rectangle.
Many graphic's updating are involved in this function.
*/
function buildRectangularPath(){
	console.log(brain.rectangularSurveyLocations)
	if(brain.rectangularSurveyLocations.length < 3){
		alert("I need 3 points for the rectangular survey")
		return
	}
	var dronesInvolved = new Array()
	for(drone in brain.drones){
		if (brain.drones[drone].surveyMode == "rectangular") {
			dronesInvolved.push(brain.drones[drone].name)
		}
	}
	//AJAX request to server for building points inside the rectangular area
	$.ajax({
		type: 'POST',
		url: '/buildRectangularPath',
		contentType: 'application/json',
		data: JSON.stringify({drones: dronesInvolved, locationsList: brain.rectangularSurveyLocations}),
		success: function(data){
			data = data['data']
			console.log(data)
			if (data['response'] == "Connection Error") {
				alert(data['body'])
				return
			}
			if (data == 'Bad') {
				alert("You need to put the points in a particular way.")
				return
			}
			if(data['response'] == "Warn"){
				alert("[WARNING] Could happen that points in the rectangle are not perferct")
			}
			locations = data['UAVs']
			for (var index in locations) {
				 var element = locations[index]
				 var indexDrone = brain.getIndexDrone(element['name'])
				 var pointsArray = element['points']
				 for (var secondIndex in pointsArray) {
					  console.log("adding to " + element['name'] + " location " + pointsArray[secondIndex])
					 	brain.drones[indexDrone].locationsToReach.push(new Location(pointsArray[secondIndex]['latitude'], pointsArray[secondIndex]['longitude'], pointsArray[secondIndex]['altitude']))
						addLocationForRectangularSurveyInTheGUI(element['name'], pointsArray[secondIndex])
				 }
				 removeVertices()
				 deleteDeleteButtonsFromTableOfLocationsToReachInRectangularSurvey()
				}

			//addAllTheLocationsForRectangularSurvey()
			//Now I need to remove the "build rectangular path" button and replace it with
			//the "flight" button
			var flightRectangularButton = "<div class='row'>" +
																			"<div class='col-lg-12'>" +
																				'<button type="button" class="btn btn-success" onclick="flightDrone(\'' +  null + '\', \'' +  'rectangular' + '\')">Flight</button>' +
																			"</div>" +
																		"</div>"
			//Just need to understand what is the child for "build rectangular path" button and remove it.
			$("#typeOfSurveyDiv").children().eq(0).children().eq(5).remove()
			$("#typeOfSurveyDiv").children().eq(0).append(flightRectangularButton)

		},
		error: function(){
			console.log("There is an error on server side in building the points for rectangular survey")
		}
	})
}
/*
This function is used for adding each location of the rectangular survey in the map and in the
table of list of locations to reach.
*/
function addLocationForRectangularSurveyInTheGUI(droneName, location){
	var xycoords = brain.converter.getXYCoordinatesFromLatitudeLongitudeCoordinates(location['latitude'], location['longitude'])
	brain.graphicBrain.addMarker(xycoords.x, xycoords.y, "location", droneName, brain.drones, 'normal', true)
	brain.graphicBrain.addLocationIntoTableOfLocationsToReach(droneName, brain.drones, location['latitude'], location['longitude'], location['altitude'], "location", "normal")

}

//function that deletes all the buttons besides each location to reach in the rectangular survey.
function deleteDeleteButtonsFromTableOfLocationsToReachInRectangularSurvey(){
	for(var index=$("#locationsToReach > tbody > tr").length-1; index>=0; index--){
			$("#locationsToReach > tbody").children().eq(index).children().eq(5).html('-')
		}
}

/*
This function removes the vertices data on the map and on the table of locations to reach. Moreover it clears the array on ClientBrain instance.
*/
function removeVertices(){
	//removing all the locations to reach from the table
	for(var index=$("#locationsToReach > tbody > tr").length-1; index>=0; index--){
			// These following 3 lines of code are used to remove the marker of the location just reached from map
			var marker = $("#locationsToReach > tbody").children().eq(index).children().eq(0).html()
			if (marker == '-') {
				var letter = $("#locationsToReach > tbody").children().eq(index).children().eq(1).html()
				var idMarker = '-' + (letter.charCodeAt()-96)
				console.log(idMarker)
				$("[id = '" + idMarker + "']").remove()
				//this line of code is used for deleting the row which represents a location just reached
				$("#locationsToReach > tbody").children().eq(index).remove()
			}
			//index = $("#locationsToReach > tbody > tr").length
		}

	brain.rectangularSurveyLocations = new Array()
}


/*
This function will be called when user presses on "Cancel" button. Basically I have to remove all the
data stored for the rectangular path and adjust every thing correllated with.
*/
function deleteDataOfRectangularSurvey(){

	//First of all removing points on the map and on the table of locations to reach shown
	for(var index=$("#locationsToReach > tbody > tr").length-1; index>=0; index--){
			// These following 3 lines of code are used to remove the marker of the location just reached from map
			var marker = $("#locationsToReach > tbody").children().eq(index).children().eq(1).html()
			if (marker.indexOf('home') == -1) {
				var id = $("#locationsToReach > tbody").children().eq(index).children().eq(0).html()
				var idMarker = id + marker
				console.log("I'm removing " + idMarker)
				$("[id = '" + idMarker + "']").remove()
				//this line of code is used for deleting the row which represents a location just reached
				$("#locationsToReach > tbody").children().eq(index).remove()
			}
			//index = $("#locationsToReach > tbody > tr").length
		}
		//removing imagea of each vertix on the map.
	for (var i = -3; i < 0; i++) {
		$("[id = '"+  i + "']").remove()
	}
	//Removing information in the table of the drones
	for(var index=0; index<$("#dronesTable > tbody > tr").length; index++){
		var buttonName = $("#dronesTable > tbody").children().eq(index).children().eq(3).text()
		// I already know that drone is connected
		if(buttonName == 'Rectangular Survey Mode'){
			var droneName = $("#dronesTable > tbody").children().eq(index).children().eq(0).text()
			var buildPathButton = '<button type="button" class="btn btn-success" onclick="buildPath(\'' +  droneName + '\')">Build Path</button>'
			$("#dronesTable > tbody").children().eq(index).children().eq(3).html(buildPathButton)
		}
	}
	//Removing data from the array of locations for the rectangular survey
	brain.rectangularSurveyLocations = new Array()
	brain.typeOfSurvey = 'normal'

	//Remobing the 'rectangular' survey mode from the drones
	for(element in brain.drones){
		if(brain.drones[element].surveyMode == 'rectangular'){
			brain.drones[element].surveyMode = 'normal'
			brain.drones[element].locationsToReach = new Array()
		}
	}
}
