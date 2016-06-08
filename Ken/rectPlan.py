from math import asin
from math import acos
from math import tan
from math import atan
from math import floor
from math import ceil
from math import pi

class latlon:
    n=float()
    w=float()
    def __init__(self, north, west):
        self.n=north
        self.w=west

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

''' Excellent Reference for checking plan point correctness:
    http://www.darrinward.com/lat-long/?id=1908337 '''

''' In each of the following cases the points on the rectangle ccw from sw most corner are given
    f1 is the field for the may 10 demo
    f2 is the field just north of that one
    f3 is a field on a strange angle I found for testing'''

f1=[latlon(38.893866,-92.201769),latlon(38.893865, -92.201024),latlon(38.894552,-92.201016),latlon(38.894554,-92.201748)]
f2=[latlon(38.894687,-92.202445),latlon(38.894659,-92.201019),latlon(38.895398,-92.201018),latlon(38.895424,-92.202389)]
f3=[latlon(38.202472,-91.736857),latlon(38.203990,-91.734097),latlon(38.205077,-91.735023),latlon(38.203475,-91.737941)]

badPoints=[latlon(38.893968,-92.201754),latlon(38.893906, -92.201759),latlon(38.894549,-92.201091),latlon(38.894549, -92.201046)]
badPoints2=[latlon(38.893866,-92.201769), latlon(38.893964, -92.201031), latlon(38.894561, -92.200889)]
def add(p1, p2):
    north=p1.n+p2.n
    west=p1.w+p2.w
    return latlon(north,west)

def sub(p1,p2):
    north=p1.n-p2.n
    west=p1.w-p2.w
    return latlon(north,west)

def sdiv(p,scalar):
    north=p.n/scalar
    west=p.w/scalar
    return latlon(north,west)

def smult(p, scalar):
    north=p.n*scalar
    west=p.w*scalar
    return latlon(north,west)

def mag(p):
    return (p.n*p.n+p.w*p.w)**.5


def isPerpendicular(p1,p2,p3):
    tolerance=.02
    v12=sub(p2,p1)
    v23=sub(p3,p2)
    v31=sub(p1,p3)
    hypotenuse=mag(v31)
    sides=(mag(v12)**2+mag(v23)**2)**.5
    if sides > hypotenuse*(1-tolerance) and sides < hypotenuse*(1+tolerance):
        return True
    else:
        return False


def rectMission(p1, p2, p3, alt, cam='gopro', imgOvr=.05):
    picList=list()
    camParam={'pi':{'ssizem':2.74, 'ssizep':3.76, 'flen':3.6, 'angN' : 0.7272647522337332, 'angW' : 0.9625338617968637, 'TangN':.8900036993, 'TangW':1.436087493},
              'canon':{'ssizem':5.7, 'ssizep':7.6, 'flen':5.2, 'angN' : 1.0027311229353408, 'angW' : 1.2621587749426584, 'TangN':1.566803225, 'TangW':3.1365079},
              'gopro':{'angN':2.792523803, 'angW':2.792523803, 'TangN':2.3857296493600746, 'TangW':2.3857296493600746}}
    if isPerpendicular(p1,p2,p3):
        v21=sub(p1,p2)
        v23=sub(p3,p2)

        vectorAngle=atan(v21.n/v21.w)*180/pi
        if v21.n<0:
            if v21.w<0:
                bearing=270-abs(vectorAngle) #quadrant 3
            else:
                bearing=90+abs(vectorAngle) #quadrant 2
        else:
            if v21.w<0:
                bearing = 270+abs(vectorAngle) #quadrant 4
            else:
                bearing = 90-abs(vectorAngle) #quadrant 1
        mdeg=110574.611
        innerspacing=alt*camParam[cam]['TangN']*(1-imgOvr)/mdeg
        outerspacing=alt*camParam[cam]['TangW']*(1-imgOvr)/mdeg
        innerstep=smult(sdiv(v21, mag(v21)),innerspacing)
        outerstep=smult(sdiv(v23, mag(v23)),outerspacing)
        innerlimit=round(mag(sub(v21,sdiv(innerstep,2)))/mag(innerstep))
        outerlimit=floor(mag(sub(v23,sdiv(outerstep,2)))/mag(outerstep))
        picNum=0
        position=add(add(p2,sdiv(outerstep,2)),sdiv(innerstep,2))
        picNum+=1
        picList.append(mission(position.n,position.w,alt,bearing,picNum))
        #print (position.n, position.w)
        #print (str(position.n)+','+str(position.w))
        for i in range(0,int(outerlimit+1)):
            for k in range(0,int(innerlimit-1)):
                if i%2==0:
                    position=add(position,innerstep)
                    #print (str(position.n)+','+str(position.w))
                else:
                    position=sub(position,innerstep)
                    #print (str(position.n)+','+str(position.w))

                picNum+=1
                picList.append(mission(position.n,position.w,alt,bearing,picNum))
            if i!= outerlimit:
                position=add(position,outerstep)
                #print (str(position.n)+','+str(position.w))
                picNum+=1
                picList.append(mission(position.n,position.w,alt,bearing,picNum))
        #print (str(position.n)+','+str(position.w), picNum)
        return picList
    else:
        print ("Error: Given points do not form a sufficiently perpindiucalr angle for optimal operation")
        return None
#missionList=rectMission(f1[0],f1[1],f1[2],20, 'pi')
#missionList=rectMission(f2[2],f2[3],f2[0],20, 'canon')
#missionList=rectMission(f3[2],f3[3],f3[0],20, 'pi')
#missionList=rectMission(f1[0],f1[1],badPoints[2],20, 'pi')
if missionList != None:
    for x in missionList:
        if x!=missionList[-1]:
            print(x.latitude,',',x.longitude)
        else:
            print(x.latitude,',',x.longitude,x.bearing,x.ordLoc)
