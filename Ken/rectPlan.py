from math import asin
from math import acos
from math import tan
from math import atan
from math import floor
from math import ceil
from math import pi

class latlon:
    n=float()
    e=float()
    def __init__(self, north, east):
        self.n=north
        self.e=east

class mission:
    latitude=float()
    longitude=float()
    altitude=float()
    bearing=float()
    ordLoc=int()
    def __init__(self, north, west, height=20, angle=0, number=0):
        self.latitude=north
        self.longitude=west
        self.altitude=height
        self.bearing=angle
        self.ordLoc=number

'''p2 must be the vertex between 1 and 3
The algorithm assumes the orientation
    of the drone is toward the first point
    from the second: the shorter dimension of the
    camera is parallel with the vector from rectangle vertex 2 to 1.'''

'''This algorithm returns a list with the first item in the list being
    the 'quality' of the generated rectangle. The values possible are
    'Good'
    'Warn'
    'Bad'
    and you can use these to decide what to do on the client side. For the Bad case,
    no missions are actually calculated since thre resulting survey will be too unstable.
    In the case of the 'Good' or 'Warn' scenarios, the rest of the items in the list
    consist  of 'missions' each with member variables latitude, longitude,
    altitude, bearing, and ordLoc. All are striaghtforward in meaning with ordLoc being the
    only exception. It denotes the position of that mission in the context of the
    larger planned survey in an ordinal manner. '''

''' Excellent Reference for checking plan point correctness:
    http://www.darrinward.com/lat-long/?id=1908337 '''

''' In each of the following cases the points on the rectangle ccw from sw most corner are given
    f1 is the field for the may 10 demo
    f2 is the field just north of that one
    f3 is a field on a strange angle I found for testing'''

f1=[latlon(38.893866,-92.201769),latlon(38.893865, -92.201024),latlon(38.894552,-92.201016),latlon(38.894554,-92.201748), latlon(38.894035, -92.200937), latlon(38.894281, -92.200959) ]
f2=[latlon(38.894687,-92.202445),latlon(38.894659,-92.201019),latlon(38.895398,-92.201018),latlon(38.895424,-92.202389)]
f3=[latlon(38.202472,-91.736857),latlon(38.203990,-91.734097),latlon(38.205077,-91.735023),latlon(38.203475,-91.737941)]
f4=[latlon(37.924969, -91.772384),latlon(37.924600, -91.772422),latlon(37.924641, -91.773143),latlon(37.925010, -91.773106), latlon(37.925031, -91.772746), latlon(37.924787, -91.772348) ]

badPoints=[latlon(38.893968,-92.201754),latlon(38.893906, -92.201759),latlon(38.894549,-92.201091),latlon(38.894549, -92.201046)]
badPoints2=[latlon(38.893866,-92.201769), latlon(38.893964, -92.201031), latlon(38.894561, -92.200889)]
def add(p1, p2):
    north=p1.n+p2.n
    west=p1.e+p2.e
    return latlon(north,west)

def sub(p1,p2):
    north=p1.n-p2.n
    west=p1.e-p2.e
    return latlon(north,west)

def sdiv(p,scalar):
    north=p.n/scalar
    west=p.e/scalar
    return latlon(north,west)

def smult(p, scalar):
    north=p.n*scalar
    west=p.e*scalar
    return latlon(north,west)

def mag(p):
    return (p.n*p.n+p.e*p.e)**.5

def isPerpendicular(p1,p2,p3):
    tightTolerance=.04
    warnTolerance=.14
    v12=sub(p2,p1)
    v23=sub(p3,p2)
    v31=sub(p1,p3)
    hypotenuse=mag(v31)
    sides=(mag(v12)**2+mag(v23)**2)**.5
    if sides > hypotenuse*(1-tightTolerance) and sides < hypotenuse*(1+tightTolerance):
        return "Good"
    elif sides > hypotenuse*(1-warnTolerance) and sides < hypotenuse*(1+warnTolerance):
        return "Warn"
    else:
        return "Bad"


def rectMission(p1, p2, p3, alt, cam='gopro', imgOvr=.05):
    rectSurvey={'response':'bad', 'picList':list()}
    camParam={'pi':{'ssizem':2.74, 'ssizep':3.76, 'flen':3.6, 'angN' : 0.7272647522337332, 'angW' : 0.9625338617968637, 'TangN':.8900036993, 'TangW':1.436087493},
              'canon':{'ssizem':5.7, 'ssizep':7.6, 'flen':5.2, 'angN' : 1.0027311229353408, 'angW' : 1.2621587749426584, 'TangN':1.566803225, 'TangW':3.1365079},
              'gopro':{'angN':2.792523803, 'angW':2.792523803, 'TangN':2.3857296493600746, 'TangW':2.3857296493600746}}
    perpendicularTestResult=isPerpendicular(p1,p2,p3)
    if perpendicularTestResult=="Good" or perpendicularTestResult=="Warn":
        v21=sub(p1,p2)
        v23=sub(p3,p2)
        rectSurvey['response']=perpendicularTestResult

        vectorAngle=atan(v21.n/v21.e)*180/pi
        if v21.n<0:
            if v21.e<0:
                bearing=270-abs(vectorAngle) #quadrant 3
            else:
                bearing=90+abs(vectorAngle) #quadrant 2
        else:
            if v21.e<0:
                bearing = 270+abs(vectorAngle) #quadrant 4
            else:
                bearing = 90-abs(vectorAngle) #quadrant 1
        mdeg=110574.611
        innerspacing=alt*camParam[cam]['TangN']*(1-imgOvr)/mdeg
        outerspacing=alt*camParam[cam]['TangW']*(1-imgOvr)/mdeg
        innerstep=smult(sdiv(v21, mag(v21)),innerspacing)
        outerstep=smult(sdiv(v23, mag(v23)),outerspacing)
        innerlimit=floor(mag(sub(v21,sdiv(innerstep,2)))/mag(innerstep))
        outerlimit=floor(mag(sub(v23,sdiv(outerstep,2)))/mag(outerstep))
        picNum=0
        position=add(add(p2,sdiv(outerstep,2)),sdiv(innerstep,2))
        picNum+=1
        rectSurvey['picList'].append(mission(position.n,position.e,alt,bearing,picNum))
        #print("pic append worked")
        #print (position.n, position.e)
        #print (str(position.n)+','+str(position.e))
        for i in range(0,int(outerlimit+1)):
            for k in range(0,int(innerlimit)):
                if i%2==0:
                    position=add(position,innerstep)
                    #print (str(position.n)+','+str(position.e))
                else:
                    position=sub(position,innerstep)
                    #print (str(position.n)+','+str(position.e))

                picNum+=1
                rectSurvey['picList'].append(mission(position.n,position.e,alt,bearing,picNum))
            if i!= outerlimit:
                position=add(position,outerstep)
                #print (str(position.n)+','+str(position.e))
                picNum+=1
                rectSurvey['picList'].append(mission(position.n,position.e,alt,bearing,picNum))
        #print (str(position.n)+','+str(position.e), picNum)
        return rectSurvey
    else:
        print ("Error: Given points do not form a sufficiently perpindiucalr angle for optimal operation")
        return perpendicularTestResult


def missionDivision(pointList, droneList):
    dividedMission={'response':pointList['response'], 'locations':list()}
    if len(droneList)==3:
        dividedMission['locations'].append({'name':dronelist[0], 'points':pointList['picList']})
        return dividedMission

    elif len(droneList)==6:
        drone1location=latlon(droneList[1],droneList[2])
        drone2location=latlon(droneList[4],droneList[5])
        numPoints=len(pointList['picList'])
        halfIndex=int(numPoints/2)
        distance4d1begd2half=mag(sub(drone1location,latlon(pointList['picList'][0].latitude, pointList['picList'][0].longitude)))+mag(sub(drone2location,latlon(pointList['picList'][halfIndex].latitude, pointList['picList'][halfIndex].longitude)))
        distance4d2begd1half=mag(sub(drone2location,latlon(pointList['picList'][0].latitude, pointList['picList'][0].longitude)))+mag(sub(drone1location,latlon(pointList['picList'][halfIndex].latitude, pointList['picList'][halfIndex].longitude)))
        if distance4d1begd2half <= distance4d2begd1half:
            dividedMission['locations'].append({'name':droneList[0], 'points':pointList['picList'][0:halfIndex]})
            dividedMission['locations'].append({'name':droneList[3], 'points':pointList['picList'][halfIndex:numPoints+1]})
        else:
            dividedMission['locations'].append({'name':droneList[3], 'points':pointList['picList'][0:halfIndex]})
            dividedMission['locations'].append({'name':droneList[0], 'points':pointList['picList'][halfIndex+1:numPoints+1]})
        return dividedMission
    else:
        print("Wrong")
        return

surveyPlan=rectMission(f4[0],f4[1],f4[2],5)
#missionList=rectMission(f2[2],f2[3],f2[0],20, 'canon')
#missionList=rectMission(f3[2],f3[3],f3[0],20, 'pi')
#missionList=rectMission(f1[0],f1[1],badPoints[2],20, 'pi')
'''
if surveyPlan != None:
    for x in surveyPlan['picList'] :
        if x!=surveyPlan['picList'][-1]:
            print(x.latitude,',',x.longitude)
        else:
            print(x.latitude,',',x.longitude,x.bearing,x.ordLoc)
'''
dlist=["gold", f4[4].n, f4[4].e, "green", f4[5].n, f4[5].e]

data=missionDivision(surveyPlan, dlist)

for location in data['locations']:
    print(location['name'])
    for point in location['points']:
        print(point.latitude, point.longitude)
