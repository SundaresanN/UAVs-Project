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


connection = Wireless()
freeInterface = ''
for interface in connection.interfaces():
    connection.interface(interface)
    print connection.current()
    if connection.current() is None:
        freeInterface = connection.interface()
        connection.interface(freeInterface)
        print  "Free interface: ", freeInterface
        break
print "Free interface: ", freeInterface
print "Current Interface: ", connection.current()
import time
cameraWiFis = ['SoloGreenCameraRGB', 'SoloGoldCameraRGB']
password = "Silvestri"
for ssid in cameraWiFis:
    print "ssid: ", ssid
    connection.connect(ssid, password)
    print "Connected to: ", connection.current()
    takeAPicture()
