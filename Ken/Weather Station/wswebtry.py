#!/usr/bin/env python
import PCF8591 as ADC
import Adafruit_DHT as DHT
import Adafruit_BMP.BMP085 as BMP085
import RPi.GPIO as GPIO
import time
from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)
humitureSensor = 11
humiturePin = 17
rainPin = 18
GPIO.setmode(GPIO.BCM)
windADCPin = 2
lightADCPin = 1

def setup():
    ADC.setup(0x48)
    GPIO.setup(rainPin, GPIO.IN)

def translate(value, leftMin, leftMax, rightMin, rightMax):
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

def destroy():
    GPIO.cleanup()

class SensorData(Resource):
    def get(self):
         print''
         print'Temp \t Humidity  \t Pressure \t Wind \t \tLight \t \t Rain? '
         sensor = BMP085.BMP085()
         temp = sensor.read_temperature()	# Read temperature to veriable temp
         pressure = sensor.read_pressure()/100.0	# Read pressure to veriable pressure
         humidity, tempWorse = DHT.read_retry(humitureSensor, humiturePin)
         windSpeed = int(round(translate(ADC.read(windADCPin), 31, 200, 0, 32.4)))
         lightIntensity = translate(ADC.read(lightADCPin), 250, 0, 0, 100)
         raining = not GPIO.input(rainPin)
         dewPoint = temp -((100.0-humidity)/5.0)
         if humidity is not None and temp is not None:
             print '{0:0.1f} C \t {1:0.1f} % \t {3:.2f} mBar \t {4:.1f} m/s \t{5:.02f} % \t {6}'.format(temp, humidity, dewPoint, pressure, windSpeed, lightIntensity, raining)
             return {'temperature' : temp, 'humidity' : humidity, 'pressure':pressure, 'wind':windSpeed, 'light':lightIntensity, 'rain':raining }
         else:
             print 'Failed to get reading. Try again!'
             return 'error'

api.add_resource(SensorData, '/')

if __name__ == "__main__":
    setup()
    try:
	    app.run(host='0.0.0.0', port=80, debug=True)
    except KeyboardInterrupt:
	    destroy()








'''def loop():
    while True:
        print''
        print'Temp \t Humidity  \t Pressure \t Wind \t \tLight \t \t Raining? '
        for x in range(0, 10):
            sensor = BMP085.BMP085()
            temp = sensor.read_temperature()	# Read temperature to veriable temp
            pressure = sensor.read_pressure()/100.0	# Read pressure to veriable pressure
            humidity, tempWorse = DHT.read_retry(humitureSensor, humiturePin)
            windSpeed = int(round(translate(ADC.read(windADCPin), 31, 200, 0, 32.4)))
            lightIntensity = translate(ADC.read(lightADCPin), 250, 0, 0, 100)
            raining = not GPIO.input(rainPin)
            dewPoint = temp -((100.0-humidity)/5.0)

            if humidity is not None and temp is not None:
                print '{0:0.1f} C \t {1:0.1f} % \t {3:.2f} mBar \t {4:.1f} m/s \t{5:.02f} % \t {6}'.format(temp, humidity, dewPoint, pressure, windSpeed, lightIntensity, raining)

            else:
                print 'Failed to get reading. Try again!' '''
