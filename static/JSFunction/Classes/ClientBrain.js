function ClientBrain(socket, map){

	//Members
	this.socket = socket

	this.map = map

	this.drones = new Array()

	this.converter = new Converter()

	this.graphicBrain = new GraphicBrain()

	//Methods
	this.initialGraphicSettings = initialGraphicSettings

	this.waitingClickOnMap = waitingClickOnMap

	this.getIndexDrone = getIndexDrone
	
}

function initialGraphicSettings(){

	this.graphicBrain.init(this.map, this.drones)

	this.waitingClickOnMap(this.graphicBrain, this.converter, this.drones)
}

function waitingClickOnMap(graphicBrain, converter, drones){
	
	$(".map").click(function(e){
		
		if(graphicBrain.clickOnMap == false){
			
			graphicBrain.clickOnMap = true
			//this.graphicBrain.clickOnMap = clickOnMap
			// this var is declared in usefulfunction.js
			parentObj = this.offsetParent;
			var x = e.pageX - parentObj.offsetLeft
			var y = e.pageY - parentObj.offsetTop
			var location = converter.getLatitudeLongitudeCoordinatesFromXYCoordinates(x, y)
			graphicBrain.showTableForLocationToAdd(location.latitude, location.longitude, drones)

		}else{
			alert("You have already clicked on map!\nYou can either fill the fields to insert the location in PoIs List or cancel the PoIs just inserted from map")
		}
		
	})

}

function getIndexDrone(droneName){

	for(index in this.drones){

		if (this.drones[index].name == droneName) {

			return index
		}
	}
	return -1
}