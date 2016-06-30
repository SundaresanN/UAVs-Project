function updateGraphicAndDataStructureInformationOnOscillationSurvey(data){
	var textToDisplay = "Oscillation Survey Data <br>" +
									"Drone " + data['name'] + "<br>" +
									" - battery: " + data['battery'] + "<br>" +
									" - #oscillations: " + data['oscillations'] + "<br>"

	textToDisplay = "Drone " + data['name'] + ' has completed its flight for the oscillation survey, now it is coming back home'
	var divToDisplay = "<div class='well well-lg'>" + textToDisplay + "</div>"
	$("#liveFlightInformation").children().eq(0).children().eq(0).children().eq(1).prepend(divToDisplay)

	var buildPathButton = '<button type="button" class="btn btn-success" onclick="buildPath(\'' +  data['name'] + '\')">Build Path</button>'
	$("[id = '" + data['name'] + "']").children().eq(3).html(buildPathButton)
	$("[id = '" + data['name'] + "']").children().eq(2).html(data['battery'])
	//Now I need to delete the markers, locations on the locations to reach table and the data on the Drone instance
	var length = $("#locationsToReach > tbody > tr").length
	for(var index=0; index<length; index++){
		var latitude = $("#locationsToReach > tbody").children().eq(index).children().eq(2).html()
		var longitude = $("#locationsToReach > tbody").children().eq(index).children().eq(3).html()
		var droneIndex = brain.getIndexDrone(data['name'])
		for (var i = 0; i < brain.drones[droneIndex].locationsToReach.length; i++) {
			if (brain.drones[droneIndex].locationsToReach[i].latitude == latitude && brain.drones[droneIndex].locationsToReach[i].longitude == longitude) {
				// These following 3 lines of code are used to remove the marker of the location just reached from map
				var marker = $("#locationsToReach > tbody").children().eq(index).children().eq(1).html()
				var idMarker = data['name'] + (marker.charCodeAt()-96)
				$("[id = '" + idMarker + "']").remove()
				//this line of code is used for deleting the row which represents a location just reached
				$("#locationsToReach > tbody").children().eq(index).remove()
				index = index-1
			}
		}
	}
	var droneIndex = brain.getIndexDrone(data['name'])
	brain.drones[droneIndex].locationsToReach = new Array()
}


function addGraphicsInfoForTheOscillationSurvey(){
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
										"<button type='button' class='btn btn-primary' id='confirmOscillationSurvey'>Confirm</button>" +
										"<button type='button' class='btn btn-danger' id='cancelOscillationSurvey'>Cancel</button>" +
									"</div>" +
								"</div>"
	$("#typeOfSurveyDiv").children().eq(0).append(buttons)

	$("#confirmOscillationSurvey").click(function(){
		var droneSelected = 0
		var child = 2
		while($('#typeOfSurveyDiv').children().eq(0).children().eq(child).children().eq(0).children().hasClass('checkbox')){
			var drone = $('#typeOfSurveyDiv').children().eq(0).children().eq(child).children().eq(0).children().eq(0).children().eq(0).text()
			var index = brain.getIndexDrone(drone)
			if ($('#typeOfSurveyDiv').children().eq(0).children().eq(child).children().eq(0).children().eq(0).children().eq(0).children().eq(0).is(':checked')) {
				droneSelected = $('#typeOfSurveyDiv').children().eq(0).children().eq(child).children().eq(0).children().eq(0).children().eq(0).text()
				break
			}
			child = child + 1
		}
		if (droneSelected == 0) {
			alert("Please insert one drone for this type of survey.")
			return
		}
		prepareOscillationSurvey(droneSelected)
		$("#confirmOscillationSurvey").remove()
	})

	$("#cancelOscillationSurvey").click(function(){
		// Removing the elements on the column of the survey's selection
		while($('#typeOfSurveyDiv').children().eq(0).children().eq(2).html() != undefined){
			$('#typeOfSurveyDiv').children().eq(0).children().eq(2).remove()
		}
		var button = "<div class='row'>" +
										"<div class='col-lg-12'>" +
											"<button type='button' class='btn btn-primary' id='confirmedSurvey' onclick='confirmedSurvey()'>Confirm</button>" +
										"</div>" +
									"</div>"
		$("#typeOfSurveyDiv").children().eq(0).append(button)

		// Now I have to remove the data from the locations to reach table and from the drone that is in the oscillation mode
		var index = -1
		for(el in brain.drones){
			if(brain.drones[el].surveyMode == 'oscillation'){
				index = el
				break
			}
		}

		console.log("Drone in oscillation mode index: " + index)
		if(index == -1){
			alert("No drone in oscillation mode")
			return
		}
		deleteDataOfOscillationSurvey(brain.drones[index].name)
	})
}

//This function will remove the graphic components in the drones table and will replace them with the components correllated with the
//retangular survey
function prepareOscillationSurvey(drone){
	//Deleting the 'build path' button, if present, on the drones table and replacing it with the string 'oscillation survey mode'
	var index = brain.getIndexDrone(drone)
	brain.drones[index].surveyMode = "oscillation"
	if($("[id = '" + brain.drones[index].name + "']").children().eq(3).children().eq(0).text() == 'Build Path'){
			var buildPathButton = '<button type="button" class="btn btn-success" onclick="buildPath(\'' +  brain.drones[index].name + '\')">Build Path</button>'
		$("[id = '" + brain.drones[index].name + "']").children().eq(3).html(buildPathButton)
	}


}

function deleteDataOfOscillationSurvey(drone){
	//First of all removing points on the map and on the table of locations to reach shown
	for(var index=$("#locationsToReach > tbody > tr").length-1; index>=0; index--){
			// These following 3 lines of code are used to remove the marker of the location just reached from map
			var marker = $("#locationsToReach > tbody").children().eq(index).children().eq(1).html()
			if (marker.indexOf('home') == -1) {
				var idMarker = drone + (marker.charCodeAt()-96)
				$("[id = '" + idMarker + "']").remove()
				//this line of code is used for deleting the row which represents a location just reached
				$("#locationsToReach > tbody").children().eq(index).remove()
			}
			//index = $("#locationsToReach > tbody > tr").length
		}

	//Removing information in the table of the drones
	for(var index=0; index<$("#dronesTable > tbody > tr").length; index++){
		var droneName = $("#dronesTable > tbody").children().eq(index).children().eq(0).text()
		// I already know that drone is connected
		if(droneName == drone){
			if($("#dronesTable > tbody").children().eq(index).children().eq(3).text() == "Connect"){
				break
			}
			var buildPathButton = '<button type="button" class="btn btn-success" onclick="buildPath(\'' +  droneName + '\')">Build Path</button>'
			$("#dronesTable > tbody").children().eq(index).children().eq(3).html(buildPathButton)
		}
	}
	//Removing data from the array of locations for the oscillation survey
	var index = brain.getIndexDrone(drone)
	brain.drones[index].locationsToReach = new Array()
	brain.typeOfSurvey = 'normal'

	//Removing the 'oscillation' survey mode from the dron
	brain.drones[index].surveyMode = 'normal'

}
