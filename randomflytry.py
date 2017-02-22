from math import asin
from math import acos
from math import tan
from math import atan
from math import floor
from math import ceil
from math import pi
from random import gauss, choice, randint
from time import time
from statistics import mean


mdeg=110574.611
mu=.6
sig=.4
class latlonalt:
    n=float()
    e=float()
    d=float()
    def __init__(self, north, east, alt):
        self.n=north
        self.e=east
        self.d=alt
    def __repr__(self):
        return str(self.n)+', '+str(self.e)
class latlon:
    n=float()
    e=float()
    def __init__(self, north, east):
        self.n=north
        self.e=east
    def __repr__(self):
        return str(self.n)+', '+str(self.e)

class mission:
    latitude=float()
    longitude=float()
    altitude=float()
    bearing=float()
    ordLoc=int()
    def __init__(self, north, east, height=20, angle=0, number=0):
        self.latitude=north
        self.longitude=east
        self.altitude=height
        self.bearing=angle
        self.ordLoc=number
    def __repr__(self):
        return str(self.latitude)+' '+str(self.longitude)+' '+str(self.altitude)

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

def randMissionGen(rad, fname, p1=latlon(37.924530, -91.772487)):
    rad=rad/mdeg
    fout=open(fname,'w')
    numPointsDesired=700
    picNum=0
    picList=[]
    distn=0
    diste=0
    disth=0
    avdisth=0
    tempn=rad*gauss(mu, sig)*choice([-1,1])
    tempe=rad*gauss(mu, sig)*choice([-1,1])
    disth=0
    avdisth=0
    while(picNum<numPointsDesired):
        tempn=rad*gauss(mu, sig)*choice([-1,1])
        tempe=rad*gauss(mu, sig)*choice([-1,1])
        picList.append(add(latlon(tempn,tempe),p1))
        picNum+=1

    for x in range(0,len(picList)-1):
        diffn=picList[x+1].n-picList[x].n
        diffe=picList[x+1].e-picList[x].e
        disth+=mag(latlon(diffn, diffe))
    altList=[]
    distv=0
    for x in range(0,numPointsDesired):
        altList.append(randint(10000,35000)/1000)
    for x in range(len(altList)-1):
        distv+=abs(altList[x+1]-altList[x])
    #print(picNum, len(picList), len(altList))
    #print(distv/(len(altList)-1))
    #print(disth*mdeg/(len(picList)-1))
    for i in range(len(picList)):
        fout.write(str(picList[i])+', '+str(altList[i])+', '+str(i)+'\n')


def randMissionRead(fname):
    randSurvey={}
    randSurvey['picList']=[]
    randSurvey['response']='Good'
    with open(fname, "r") as fin:
        for line in fin:
            tmpstr=line
            tempstr=tmpstr.strip('\n').split(',')
            randSurvey['picList'].append(mission(float(tempstr[0]),float(tempstr[1]),float(tempstr[2]),0,int(tempstr[3])))
    return randSurvey

randMissionGen(10, 'randMission.txt')
randomSurveyLocation = randMissionRead('randMission.txt')

'''
[RICCARDO] I needed this printing for the testing purposes
'''
locations = []
for location in randomSurveyLocation['picList']:
    '''
    location is a mission class instance. I can access to the single location values in a simple way:
    - location.latitude
    - location.longitude
    - location.altitude
    '''
    locations.append({
        "latitude" : location.latitude,
        "longitude": location.longitude,
        "altitude": location.altitude
        })

print locations
