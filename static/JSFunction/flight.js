function flightDrone(droneName){

	index = brain.getIndexDrone(droneName)

	brain.drones[index].flight(brain.socket)
}

