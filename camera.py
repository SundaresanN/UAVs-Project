from goprohero import GoProHero
import time

class Camera:
    def __init__(self, interface, wifi, name):
        self.camera = GoProHero(password='Silvestri')
        self.name = name + " Camera"
        self.networkInterface = interface
        self.wifiNetwork = wifi

    def takeAPicture(self, connectionManager):
        self.__connectToMyNetwork__(connectionManager)
        '''
        You need to be sure that the GoPro is in "Photo mode"
        Check the API
        '''

        if self.camera.command('record', 'on'):
            print "Just took a picture from ", self.name
        else:
            print "error from ", self.name
        time.sleep(2)

    def __connectToMyNetwork__(self, connectionManager):
		connectionManager.interface(self.networkInterface)
		connectionManager.connect(ssid = self.wifiNetwork, password = "Silvestri")
