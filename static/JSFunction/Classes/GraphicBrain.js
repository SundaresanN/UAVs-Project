function GraphicBrain(){

	this.firstLocationAdded = false

	this.clickOnMap = false

	this.init = init

	this.addMarker = addMarker

	this.showTableForLocationToAdd = showTableForLocationToAdd

	this.addLocationIntoTableOfLocationsToReach = addLocationIntoTableOfLocationsToReach

}

function init(map, drones){

	var image = "<div class='col-lg-6' id='mapBox'><img src='" + map.imagePath + "' class='map'/></div>"

	$("#firstRow").append(image)

	var dronesTable = "<div class='col-lg-4' id='secondColumnOfFirstRow'>" +
						"<div class='row'>" +
							"<h2>Drones</h2>" +
							"<table id='dronesTable' class='table table-striped' style='width: 100%;''>" +
								"<thead>" +
					              "<tr>" +
					                "<th>Drone</th>" +
					                "<th>Drone Status</th>" +
													"<th>Drone Battery</th>" +
					                "<th>Action</th>" +
													"<th>Camera Status</th>" +
					              "</tr>" +
					            "</thead>" +
					            "<tbody>" +

					            "</tbody>" +
							"</table>" +
						"</div>" +
					  "</div>"

	$("#firstRow").append(dronesTable)
	for(element in drones){

		var button = '<button type="button" class="btn btn-success" onclick="connectDrone(\'' +  drones[element].name + '\')">Connect</button>'
		var row = "" +
			"<tr id='" + drones[element].name + "'>" +
				"<td>" + drones[element].name +"</td>" +
				"<td> Not connected </td>" +
				"<td> - </td>" +
			  '<td><button type="button" class="btn btn-success" onclick="connectDrone(\'' +  drones[element].name + '\')">Connect</button></td>' +
				"<td> - </td>" +
			"</tr>"
        $("dronesTable, tbody").append(row)
	}

	var typeOfSurveyDiv = "" +
					"<div class='col-lg-2' id='typeOfSurveyDiv'> " +
						"<div class='container-fluid'>" +
							"<div class='row'>" +
								"<div class='col-lg-12'>" +
									"<h2> Type of Survey </h2>" +
								"</div>" +
							"</div>" +
							"<div class='row'>" +
								"<div class='col-lg-12'>" +
									"<div class='form-group'>" +
										"<br />" +
										"<label for='selectTypeOfSurvey'>Select type of survey:</label>" +
										"<select class='form-control' id='selectTypeOfSurvey'> " +
											"<option>Normal Survey</option>" +
											"<option>Rectangular Survey</option>" +
											"<option>Oscillation Survey</option>" +
										"</select>" +
									"</div>" +
								"</div>" +
							"</div>" +
							/*
							"<div class='row'>" +
								"<div class='col-lg-12'>" +
									"<button type='button' class='btn btn-primary' id='confirmedSurvey' onclick='confirmedSurvey()'>Confirm</button>" +
								"</div>" +
							"</div>" +
						*/
						"</div>" +
					"</div>"
	$("#firstRow").append(typeOfSurveyDiv)
	$("#selectTypeOfSurvey").click(function(){
			confirmingSurvey()
	})
	var liveFlightInformations = "" +
		"<div id='liveFlightInformation' class='col-lg-6' style='width: 45%;>" +
					"<div class='container-fluid pre-scrollable'>" +
						"<div class='row'>" +
							"<div class='col-lg-12'>" +
								"<div class='container-fluid'>" +
									"<h2> Live Flight Information </h2>" +
								"</div>" +
								"<div class='container-fluid'>" +
							 		"<div class='well well-lg'>In this section will be displayed all the information sent by drones in flight</div>" +
								"</div>" +
							"</div>" +
						"</div>" +
					"</div>" +
				"</div>"
	$("#secondRow").append(liveFlightInformations)
}

function addMarker(x, y, typeOfMarker, droneName, drones, typeOfSurvey, camera){

	var id = droneName
	var iconPath = ""
	switch(typeOfMarker){
		case "home":
			id = id + " " + typeOfMarker
			iconPath = id
			break
		case "drone":
			id = id + " " + typeOfMarker
			iconPath = id
			console.log(id)
			break
		case "location":
			var size = 0
			if (typeOfSurvey == 'rectangular') {
				size += brain.rectangularSurveyLocations.length
			}
			if (typeOfSurvey == 'normal' || typeOfSurvey == 'oscillation') {
				for(drone in drones){
					size += drones[drone].locationsToReach.length
				}
			}
			id = id + size
			iconPath = size
			break
	}
	if (typeOfSurvey == 'rectangular') {
		var marker = "<img id='" + id + "' src='static/Images/Useful\ Images/" + iconPath + ".png' style='position: absolute' />"
		$('#mapBox').append(marker)
		$("[id='" + id + "']").css({top: y, left: x})
		return
	}
	var identificator = id.split(' ')
	identificator = identificator[1].match(/\d+/)
	var color = droneName.split(' ')
	color = color[1].toLowerCase()

	var marker = "<p id='" + id + "' style='position: absolute'>" + identificator + "</p>"
	$('#mapBox').append(marker)
	$("[id='" + id + "']").css({top: y, left: x, color: color})
	$("[id='" + id + "']").css("background-color", "black")
	$("[id='" + id + "']").css("font-size", "10pt")
	$("[id='" + id + "']").css("font-weight", "bold")

}

function showTableForLocationToAdd(latitude, longitude, drones){

	var directionInfoLatLon = "" +
		"<div id='tableInfo' class='col-lg-6' style='width: 45%;'>" +
	        "<h3>Update Info</h3>" +
	        "<div class='form-group'>" +
	            "<label for='latitude'>Latitude</label>" +
	            "<input class='form-control' id='latitude' readonly='true'>" +
	        "</div>" +
	        "<div class='form-group'>" +
	           "<label for='longitude'>Longitude</label>" +
	           "<input class='form-control' id='longitude' readonly='true'>" +
	        "</div>" +
	        "<div class='form-group'>"+
	            "<label for='altitude'>Altitude</label>" +
	            "<input type='number' min='0' class='form-control' id='altitude' value='0'>" +
	        "</div>"+
	        "<div class='form-group'>"+
	            "<label for='selectDrone'>Select Drone</label>"+
	            "<select class='form-control' id='selectDrone'>"+

	            "</select>"+
	        "</div>"+
	        "<div class='form-group' align='center'>"+
	          "<button type='button' class='btn btn-success' onclick='addLocation()'>Confirm</button>"+
	          "<button type='button' class='btn btn-danger' onclick='cancelAdding()'>Cancel</button>"+
	        "</div>"+
	      "</div>"

	$("#secondRow").append(directionInfoLatLon)

	$("#latitude").val(latitude)
	$("#longitude").val(longitude)
	/*
	this if allows me to discriminate between the normal survey mode. If suervy mode is setted as normal mode,
	user will decide which drone has to reach location that I'm adding; otherwise if the survey mode is setted as rectangular, I cannot show the drones in the select list, this
	because server will decide how to split locations to drones involved in the rectangular survey
	*/
	if(brain.typeOfSurvey == 'normal'){
		for(index in drones){
			$("#selectDrone").append("<option>" + drones[index].name + "</option>")
		}
	}
	if (brain.typeOfSurvey == "rectangular") {
		//check if a location has been already added
		if (brain.rectangularSurveyLocations.length>0) {
			$("#altitude").attr("readonly", true)
			$("#altitude").val(brain.rectangularSurveyLocations[0].altitude)
		}
		$("#selectDrone").parent().remove()
	}
	if(brain.typeOfSurvey == 'oscillation'){
		for(index in drones){
			if (brain.drones[index].surveyMode == 'oscillation') {
				$("#selectDrone").append("<option>" + drones[index].name + "</option>")
				//Adding the NED coordinates that i need for the second point
				var NEDCoordinates = "<div class='form-group'>"+
																"<label for='north'>North</label>" +
																"<input type='number' class='form-control' id='north' value='0'>" +
														"</div>"+
														"<div class='form-group'>"+
																"<label for='east'>East</label>" +
																"<input type='number' class='form-control' id='east' value='0'>" +
														"</div>"+
														"<div class='form-group'>"+
																"<label for='down'>Down</label>" +
																"<input type='number' class='form-control' id='down' value='0'>" +
														"</div>"
				$("#tableInfo").children().eq(4).after(NEDCoordinates)
			}
		}
	}
}

function addLocationIntoTableOfLocationsToReach(droneName, array, latitude, longitude, altitude, type, typeOfSurvey){

	if(this.firstLocationAdded == false){

		this.firstLocationAdded = true
		//add table
		var tableOfAllTheLocationsToReach = " " +
			"<div class='row pre-scrollable' >" +
					"<h2>Locations To Reach</h2>" +
					"<table id='locationsToReach' class='table table-striped' style='width: 80%;''>" +
						"<thead>" +
			              "<tr>" +
			              	"<th>Drone</th>" +
			              	"<th>Marker</th>" +
			                "<th>Latitude</th>" +
			                "<th>Longitude</th>" +
			                "<th>Altitude</th>" +
			                "<th>Action</th>" +
			              "</tr>" +
			        "</thead>" +
			        "<tbody>" +

			        "</tbody>" +
					"</table>" +
				"</div>"

		$("#secondColumnOfFirstRow").append(tableOfAllTheLocationsToReach)
	}

	var size = 0
	if (typeOfSurvey == "normal" || typeOfSurvey == 'oscillation') {
		for(drone in array){
			size += array[drone].locationsToReach.length
		}
	}
	//In this case array will represent rectangularSurveyLocations of ClientBrain instance
	if (typeOfSurvey == "rectangular") {
		size += array.length
	}
	var buttonDelete = '<button type="button" class="btn btn-danger" onclick="deleteLocation(\'' +  droneName + '\', \'' +  latitude + '\', \'' +  longitude + '\')">Delete</button>'
	if(type == "location"){
		//var marker = String.fromCharCode(96 + size)
		var marker = size
	}
	if (type == "home") {
		var	marker = droneName + " home"
		buttonDelete = '-'
	}
	var locationToAppend = "<tr>" +
								"<td>"+ droneName +"</td>" +
			                    "<td>"+ marker +"</td>" +
			                    "<td>"+ latitude +"</td>" +
			                    '<td> ' + longitude + '</td>' +
			                    '<td> ' + altitude + '</td>' +
			                    "<td>" +
															buttonDelete +
			                    "</td>" +
                      		"</tr>"

	$("#locationsToReach tbody").append(locationToAppend)

}

/*
################## function for some graphical modifies #################
*/

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
				var idMarker = $("#locationsToReach > tbody").children().eq(index).children().eq(0).html() + marker
				$("[id = '" + idMarker + "']").remove()
				//this line of code is used for deleting the row which represents a location just reached
				$("#locationsToReach > tbody").children().eq(index).remove()
			}
			//index = $("#locationsToReach > tbody > tr").length
		}
}
