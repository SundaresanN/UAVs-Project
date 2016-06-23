function Converter(){


	this.getXYCoordinatesFromLatitudeLongitudeCoordinates = getXYCoordinatesFromLatitudeLongitudeCoordinates

	this.getLatitudeLongitudeCoordinatesFromXYCoordinates = getLatitudeLongitudeCoordinatesFromXYCoordinates

	this.convertNEDCoordinatesInLatLonAltCoordinates = convertNEDCoordinatesInLatLonAltCoordinates
}


function getXYCoordinatesFromLatitudeLongitudeCoordinates(latitude, longitude){

	var s = Math.min(Math.max(Math.sin(brain.map.centerLatitude * (Math.PI / 180)), -.9999), .9999)

  	var tiles = 1 << brain.map.zoom

	  var centerPoint={
	    x: 128 + brain.map.centerLongitude * (256/ 360),
	    y: 128 + 0.5 * Math.log((1 + s) / (1 - s)) * -(256 / (2 * Math.PI))
	  }


	  var mouseXY = {
	    x: tiles * ((256/360)*longitude + 128),
	    y: tiles * (128 - ( (256 / (2*Math.PI)) * Math.log ( Math.tan( (Math.PI/4) + ( (Math.PI/360)*latitude) ) ) ) )
	  }


	  var mousePoint = {
	    x: mouseXY.x - (centerPoint.x*tiles),
	    y: mouseXY.y - (centerPoint.y*tiles)
	  }

	  var coordinatesXY = {
	    x: mousePoint.x + (brain.map.width/2),
	    y: mousePoint.y + (brain.map.height/2)
	  }

	  return coordinatesXY
}

function getLatitudeLongitudeCoordinatesFromXYCoordinates(mouseX, mouseY){

	var x = mouseX-(brain.map.width/2)
	var y = mouseY-(brain.map.height/2)

	var s = Math.min(Math.max(Math.sin(brain.map.centerLatitude * (Math.PI / 180)), -.9999), .9999)

	var tiles = 1 << brain.map.zoom

	var centerPoint={
	   x: 128 + brain.map.centerLongitude * (256/ 360),
	   y: 128 + 0.5 * Math.log((1 + s) / (1 - s)) * -(256 / (2 * Math.PI))
	}

	var mousePoint={
	   x:(centerPoint.x*tiles)+x,
	   y:(centerPoint.y*tiles)+y
	}

	var mouseLatLng={
	  latitude:(2 * Math.atan(Math.exp(((mousePoint.y/tiles) - 128) / -(256/ (2 * Math.PI)))) - Math.PI / 2)/ (Math.PI / 180),
	  longitude:(((mousePoint.x/tiles) - 128) / (256 / 360))
	}

	return mouseLatLng;
}

/*
	- original_location is a Location object
	this function returns a Location object
*/
function convertNEDCoordinatesInLatLonAltCoordinates(original_location, north, east, down){

	var earth_radius = 6378137.0
	var dLat = north/earth_radius
	var dLon = east/(earth_radius*Math.cos(Math.PI*original_location.latitude/180))

	var newLat = original_location.latitude + (dLat * 180/Math.PI)
	var newLon = original_location.longitude + (dLon * 180/Math.PI)
	var newAlt = original_location.altitude - down

	return new Location(newLat, newLon, newAlt)
}
