import urllib2.request

wifipassword = "09021967"
#wifipassword = "Silvestri"
on = "http://10.5.5.9/bacpac/PW?t=" + wifipassword + "&p=%01"
off = "http://10.5.5.9/bacpac/PW?t=" + wifipassword + "&p=%00"
shutter = "http://10.5.5.9/bacpac/SH?t=" + wifipassword + "&p=%01"

def SendCmd(cmd):
  data = urllib2.request.urlretrieve(cmd)


SendCmd(shutter)
