function checkOldSurvey(){
  $.ajax({
		type: 'GET',
		url: '/checkOldSurvey',
		contentType: 'application/json',
		success: function(data){
      data = data['data']
      if(data=="No old survey to end"){
        alert(data)
        return
      }
		  removingAllTheOldStuffs()
      locations = data['UAVs']
      console.log(locations)
			for (var index in locations) {
				 var element = locations[index]
         if (locations[index]['completed'] == false) {
           console.log("HERE")
           var indexDrone = brain.getIndexDrone(element['name'])
  				 var pointsArray = element['points']
  				 for (var secondIndex in pointsArray) {
  					  //console.log("adding to " + element['name'] + " location " + pointsArray[secondIndex])
  					 	brain.drones[indexDrone].locationsToReach.push(new Location(pointsArray[secondIndex]['latitude'], pointsArray[secondIndex]['longitude'], pointsArray[secondIndex]['altitude']))
  						addLocationForRectangularSurveyInTheGUI(element['name'], pointsArray[secondIndex])
  				 }
  				 //removeVertices()
  				 deleteDeleteButtonsFromTableOfLocationsToReachInRectangularSurvey()
  				}
         }
         if (locations.length > 0) {
           //Now I need to remove the "build rectangular path" button and replace it with
     			//the "flight" button
           var flightRectangularButton = "<div class='row'>" +
     																			"<div class='col-lg-12'>" +
     																				'<a type="button" class="btn btn-default" onclick="flightDrone(\'' +  null + '\', \'' +  'rectangular' + '\')">Start Survey</a>' +
     																			"</div>" +
     																		"</div>"
     			//Just need to understand what is the child for "build rectangular path" button and remove it.
     			$("#typeOfSurveyDiv").children().eq(0).children().eq(2).remove()
     			$("#typeOfSurveyDiv").children().eq(0).append(flightRectangularButton)
         }
		},
		error: function(){
      alert("There was an error on server side, function checkOldSurvey")
		}
	})
}
