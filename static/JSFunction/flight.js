/*
This function is based on the idea of communicate with server for building the locations to reach for the drone in flight.
On the server side a scheduling algorithm will be implemented in order to build a smart path of locations that drones will reach.
*/
function buildPath(droneName){

	var index = brain.getIndexDrone(droneName)
	if(brain.drones[index].locationsToReach.length == 0){
		alert("This drone has not locations to reach right now..")
		return
	}

	$.ajax({
		type: 'POST',
		url: '/buildPath',
		contentType: 'application/json',
		data: JSON.stringify({ droneName: droneName, locationsList: brain.drones[index].locationsToReach}),
		success: function(data){
			data = data['path']

			var element = brain.getIndexDrone(data['drone'])
			//adding the flight button in the dronesTable
			var flightButton = '<button type="button" class="btn btn-success" onclick="flightDrone(\'' +  brain.drones[element].name + '\')">Flight</button>'
			$("[id = '" + data['drone'] + "']").children().eq(3).html(flightButton)

		},
		error: function(){
			console.log("There is an error on server side")
		}
	})
}

/*
This function communicates with the server for handling the floght of the drone.
An AJAX request will be sent for starting the flight.
When drone is on flight, it will send information about its location or its succes on flight via socket.

*/
function flightDrone(droneName){

	var index = brain.getIndexDrone(droneName)

	//I need to check if the two points flight is checked, and if it is I need to check if the drone has at least to points to reach
	if ($("[id = '" + droneName + "']").children().eq(6).children().eq(0).prop('checked') == true){

		if (brain.drones[index].locationsToReach.length < 2){
			alert(droneName + " cannot flight in 'two points flight' mode because this drone has not enough points(at least 2)")
			$("[id = '" + droneName + "']").children().eq(6).children().eq(0).prop('checked', false)
			return
		} else{
			$.ajax({
				type: 'POST',
				url: '/twoPointsFlight',
				contentType: 'application/json',
				data: JSON.stringify({ name: droneName }),
				success: function(data){
					console.log(data)
					/*
					var element = brain.getIndexDrone(data['drone'])
					//adding the flight button in the dronesTable
					var flightButton = '<button type="button" class="btn btn-success" onclick="flightDrone(\'' +  brain.drones[element].name + '\')">Flight</button>'
					$("[id = '" + data['drone'] + "']").children().eq(3).html(flightButton)
					*/
				},
				error: function(){
					console.log("There is an error on server side")
				}
			})

			/*
			brain.socket.emit('two points flight', {'name' : droneName}, function(){
					alert("Drone is flying with Two Points Flight..")
				})
			*/
			}
	} else {
		//This means that I have a "normal" flight to accomplish
		//brain.socket.emit('flight', {'name': droneName})
		$.ajax({
			type: 'POST',
			url: '/flight',
			contentType: 'application/json',
			data: JSON.stringify({ name: droneName }),
			success: function(data){
				console.log(data)
			},
			error: function(){
				console.log("There is an error on server side")
			}
		})
	}

	brain.socket.on('Flight Information ' + droneName, function(data){
		console.log("I'm here in Flight Information " + droneName + ", numberOfTimes: " + numberOfTimes)
		var textToDisplay = "Drone " + data['name'] + "<br>" +
										"Drone location: " + "<br>" +
										" - latitude: " + data['location'][0] + "<br>" +
										" - longitude: " + data['location'][1] + "<br>" +
										" - altitude: " + data['location'][2] + "<br>"
		if (data['reached'] == true) {
			textToDisplay += "Reached location: " + data["reached"] + "<br>"
			//something to delete the location to the table
			updateGraphicAndDataStructureInformationsOnReachedLocation(data)
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
function updateGraphicAndDataStructureInformationsOnReachedLocation(data){

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

/********************************** RECTANGULAR SURBEY *************************************/
/*
When I'm in rectangular survey mode, only drones involved in it can fly. The others must wait the end of rectangular survey.
*/
function confirmedSurvey(){

	var typeOfSurvey = $("#selectTypeOfSurvey option:selected").text()
	switch (typeOfSurvey) {
		case 'Normal Survey':
			console.log(typeOfSurvey)
			brain.typeOfSurvey = 'normal'
			break;
		case 'Rectangular Survey':
			console.log(typeOfSurvey)
			//Setting up this data member of the ClientBrain instance, I set up the rectangular survey mode, so only the drones involved in
			// it can fly, the others must wait the end of the rectangular surbey flight.
			brain.typeOfSurvey = 'rectangular'
			addGraphicsInfoForTheFlightSurvey()
			alert("You need to be connected with all the drones for having success with this kind of survey. So before you start to check the drone you want in the rectangular survey, please connect every drone available")
			break;
			}
}

function addGraphicsInfoForTheFlightSurvey(){
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
			prepareSurvey(dronesSelected)
		})
}


function prepareSurvey(drones){
	//Adding button for building the rectangular path
	var buildRectangularPathButton = "<div class='row'>" +
													"<div class='col-lg-12'>" +
														'<button type="button" class="btn btn-success" onclick="buildRectangularPath()">Build Rectangular Path</button>' +
													"</div>" +
												"</div>"

	$("#typeOfSurveyDiv").children().eq(0).append(buildRectangularPathButton)
	//Deleting the 'build path' buttons, if present, on the drones table and replacing them with the string 'rectangular survey mode'
	for(element in drones){
		var index = brain.getIndexDrone(drones[element])
		brain.drones[index].surveyMode = "rectangular"
		if($("[id = '" + drones[element] + "']").children().eq(3).children().eq(0).text() == 'Build Path'){
			$("[id = '" + drones[element] + "']").children().eq(3).html('Rectangular Survey Mode')
		}
	}
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
				var idMarker = '-' + (marker.charCodeAt()-96)
				$("[id = '" + idMarker + "']").remove()
				//this line of code is used for deleting the row which represents a location just reached
				$("#locationsToReach > tbody").children().eq(index).remove()
			}
			//index = $("#locationsToReach > tbody > tr").length
		}

	//Removing information in the table of the drones
	for(var index=0; index<$("#dronesTable > tbody > tr").length; index++){
		var buttonName = $("#dronesTable > tbody").children().eq(index).children().eq(3).text()
		// I already know that drone is connected
		if(buttonName == 'Rectangular Survey Mode'){
			var buildPathButton = '<button type="button" class="btn btn-success" onclick="buildPath(\'' +  brain.drones[element].name + '\')">Build Path</button>'
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
		}
	}
}

function buildRectangularPath(){
	console.log(brain.rectangularSurveyLocations)
	if(brain.rectangularSurveyLocations.length < 3){
		alert("I need 3 points for the rectangular survey")
		return
	}
}

//This function removes from locations to reach table all the elements, but not the home location rows.
//Moreover it delete all the elements from the map and set to empty the array of locations to reach for eache drone.
function removingAllTheOldStuffs(){
	//emptying the array of locations to reach for each drone
	for (var i = 0; i < brain.drones.length; i++) {
		brain.drones[i].locationsToReach = new Array()
	}
	//removing all the locations to reach from the table
	for(var index=$("#locationsToReach > tbody > tr").length-1; index>=0; index--){
			// These following 3 lines of code are used to remove the marker of the location just reached from map
			var marker = $("#locationsToReach > tbody").children().eq(index).children().eq(1).html()
			if (marker.indexOf('home') == -1) {
				var idMarker = $("#locationsToReach > tbody").children().eq(index).children().eq(0).html() + (marker.charCodeAt()-96)
				$("[id = '" + idMarker + "']").remove()
				//this line of code is used for deleting the row which represents a location just reached
				$("#locationsToReach > tbody").children().eq(index).remove()
			}
			//index = $("#locationsToReach > tbody > tr").length
		}
}
