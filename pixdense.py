'''Takes as a parameter an integer representing the desired number of pixels per centimeter and
returns the necessary altitude from which the pictures should be taken in meters
The camera to be selected from gopro canon or pi is also user configurable, but
is defaulted to gopro for ease and current system configuration'''

def findAltitudeFromDensityDesiredByThisParticularIndividualUserMakingUseOfTheWebApplicationAtThisParticularTime(pixDense, cam='gopro'):
    from math import sqrt
    camParam={'pi':{'ssizem':2.74, 'ssizep':3.76, 'flen':3.6, 'angN' : 0.7272647522337332, 'angW' : 0.9625338617968637, 'TangN':.8900036993, 'TangW':1.436087493, 'res':5000000},
              'canon':{'ssizem':5.7, 'ssizep':7.6, 'flen':5.2, 'angN' : 1.0027311229353408, 'angW' : 1.2621587749426584, 'TangN':1.566803225, 'TangW':3.1365079, 'res':12000000},
              'gopro':{'angN':2.792523803, 'angW':2.792523803, 'TangN':2.3857296493600746, 'TangW':2.3857296493600746, 'res':12000000}}
    pixDense*=10000
    return sqrt(camParam[cam]['res']/(pixDense*camParam[cam]['TangN']*camParam[cam]['TangW']))


print(findAltitudeFromDensityDesiredByThisParticularIndividualUserMakingUseOfTheWebApplicationAtThisParticularTime(1))
