function openSocket(drone_name){

  brain.socket.on('Flight live information ' + drone_name, function(data){
    if (data['completed']==true) {

    } else{
      updateDataAndUIDuringAFlight(drone_name, data)
    }
  })
}

function updateDataAndUIDuringAFlight(drone_name, data){

}
