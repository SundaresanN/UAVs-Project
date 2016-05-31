from math import exp
mdeg=110574.611

class latlon:
    n=float()
    w=float()
    def __init__(self, north=0, west=0):
        self.n=north
        self.w=west

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

class aerobot:
    ploc=latlon()
    maxVelocityKnots=97
    def __init__(self, n=0, w=0):
        self.ploc(n,w)


    def destVec(self, dest):
        destvec=sub(dest,self.ploc)
        magdestvec=mag(destvec)
        magdestm=magdestvec*mdeg
        vel2dest=maxVelocityKnots*(1-exp(-magdestm))
        print(vel2dest)
        return div(destvec, magdestvec), vel2dest/60

    def avVec(self, aeroLocs):
        sumAvVecs=latlon()
        for uav in aeroLocs:
            avVec=sub(self.ploc, uav)
            avVecMag=mag(avVec)
            avVecMagm=avVecMag*mdeg
            velAv=maxVelocityKnots*(exp(-(avVecMagm-5))
            if avVecMagm >= 1 :
                sum(sumAvVecs, mult(div(avVec, avVecMag),velAv/60)
        return sumAvVecs



f1=latlon(37.924597, -91.772413)
f2=latlon(37.924971, -91.772383)
f3=latlon(37.925013, -91.773109)
f4=latlon(37.924646, -91.773141)

#def flight(numUavs=2, start, stop):
