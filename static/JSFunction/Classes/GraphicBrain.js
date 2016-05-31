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

	var dronesTable = "<div class='col-lg-6' id='secondColumnOfFirstRow'>" +
						"<div class='row'>" +
							"<h2>List of Drones Available</h2>" +
							"<table id='dronesTable' class='table table-striped' style='width: 80%;''>" +
								"<thead>" +
					              "<tr>" +
					                "<th>Drone</th>" +
					                "<th>Drone Status</th>" +
													"<th>Drone Battery</th>" +
					                "<th>Action</th>" +
													"<th>Camera Status</th>" +
													"<th>Camera Battery</th>" +
													"<th>Two Points Flight</th>" +
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
				"<td> - </td>" +
				"<td><input type='checkbox'></td>" +
			"</tr>"
        $("dronesTable, tbody").append(row)
	}

	var liveFlightInformations = "" +
		"<div id='liveFlightInformations' class='col-lg-6' style='width: 45%;>" +
					"<div class='container-fluid pre-scrollable'>" +
						"<h2> Live Flight Informations </h2>" +
						"<div class='container-fluid'>" +
					 		"<div class='well well-lg'>In this section will be displayed all the informations sent by drones in flight</div>" +
						"</div>" +
					"</div>" +
				"</div>"
	$("#secondRow").append(liveFlightInformations)
}

function addMarker(x, y, typeOfMarker, droneName, drones){

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
			break
		case "location":
			var size = 0
			for(drone in drones){
				size += drones[drone].locationsToReach.length
			}
			id = id + size
			iconPath = size
			break
	}

	var marker = "<img id='" + id + "' src='static/Images/Useful\ Images/" + iconPath + ".png' style='position: absolute' />"
	$('#mapBox').append(marker)
	$("[id='" + id + "']").css({top: y, left: x})

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
	            "<label for='selectCamera'>Select Drone</label>"+
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

	for(index in drones){

		$("#selectDrone").append("<option>" + drones[index].name + "</option>")

	}

}

function addLocationIntoTableOfLocationsToReach(droneName, drones, latitude, longitude, altitude, type){

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
	for(drone in drones){
		size += drones[drone].locationsToReach.length
	}
	if(type == "location"){
		var marker = String.fromCharCode(96 + size)
	}
	if (type == "home") {
		var	marker = droneName + " home"
	}

	var buttons = " - "
	var locationToAppend = "<tr>" +
								"<td>"+ droneName +"</td>" +
			                    "<td>"+ marker +"</td>" +
			                    "<td>"+ latitude +"</td>" +
			                    '<td> ' + longitude + '</td>' +
			                    '<td> ' + altitude + '</td>' +
			                    "<td>" +
			                 		buttons
			                    "</td>" +
                      		"</tr>"

	$("#locationsToReach tbody").append(locationToAppend)

}
