from wireless import Wireless
import urllib
def takeAPicture():
	wifipassword = "Silvestri"

	on = "http://10.5.5.9/bacpac/PW?t=" + wifipassword + "&p=%01"
	off = "http://10.5.5.9/bacpac/PW?t=" + wifipassword + "&p=%00"
	shutter = "http://10.5.5.9/bacpac/SH?t=" + wifipassword + "&p=%01"

	opener = urllib.FancyURLopener({})
	f = opener.open(shutter)
	print "Just took a picture"

c2 = Wireless()
c1 = Wireless()
import time
for i in range(0,20):
    c2.interface('wlx40a5ef04033b')
    time.sleep(2)
    c2.connect(ssid = 'SoloGreenCameraRGB', password = 'Silvestri')
    takeAPicture()
    print c2.current()

    c1.interface('wlx40a5ef03ea3a')
    time.sleep(2)
    c1.connect(ssid = 'SoloGoldCameraRGB', password = 'Silvestri')
    takeAPicture()
    print c1.current()
    print i
