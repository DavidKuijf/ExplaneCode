from flask import Flask , request
from flask_table import Table, Col
import json

app = Flask(__name__)
items = []


# Declare your table
class RecordTable(Table):
    planeIcao24 = Col('planeIcao24')
    planeCallsign = Col('planeCallsign')
    planeVelocity = Col('planeVelocity')
    planeVerticalRate = Col('planeVerticalRate')
    planeCountry = Col('planeCountry')
    maxDecibels = Col('maxDecibels')
    captureFormattedDate = Col('captureFormattedDate')
    captureFormattedTime = Col('captureFormattedTime')
    calculatedPlaneDistance = Col('calculatedPlaneDistance')
    planeAlt = Col('planeAlt')

@app.route('/')
def showtable():
    data = '''{
            "partitionkey": "1.11 Test", 
            "rowkey": "RegisterFunction", 
            "captureTimestamp": 1569569056, 
            "captureType": "automatic", 
            "captureFormattedDate": "20190927", 
            "captureFormattedTime": "09:24:15", 
            "maxDecibels": 58, 
            "decibelsArray": [50.9, 51.3, 56.0, 52.3, 47.9, 53.0, 57.9, 50.5, 47.1, 49.1, 50.0, 49.3, 48.7, 43.3, 44.1, 44.6, 48.3, 50.4, 44.2, 42.7], 
            "averageSampleRollupDurationInMs": 1000, 
            "sampleDurationInMs": 13000, 
            "myLat": 52.13, 
            "myLng": 4.76, 
            "myAlt": 0, 
            "deviceCordova": "", 
            "deviceModel": "Raspberry Pi Model B Plus Rev 1.2", 
            "devicePlatform": "Raspbian GNU/Linux 9.4", 
            "deviceVersion": "9.4", 
            "deviceManufacturer": "Raspberry pi", 
            "deviceIsVirtual": false, 
            "deviceSerial": "b8:27:eb:68:ef:78", 
            "planeIcao24": "484b2a", 
            "planeCallsign": "TRA5955 ", 
            "planeCountry": "Kingdom of the Netherlands", 
            "planeLat": 52.144, 
            "planeLng": 4.7974, 
            "planeAlt": 2255.52, 
            "planeTimePosition": 1569569049, 
            "planeOnGround": false, 
            "planeVelocity": 118.86, 
            "planeTrueTrack": 185.46, 
            "planeVerticalRate": 15.93, 
            "planeSquawk": "2144", 
            "planeSpi": false, 
            "planePositionSource": 0, 
            "calculatedPlaneDistance": 3649, 
            "appVersion": "1.00 PI Test"}'''
    
    print(items)
    table = RecordTable(items , border=True)
    
    return table.__html__()

@app.route('/submit', methods=['POST'])
def submit():
    loadedjson = request.json
    #loadedjson = json.loads(data)
    items.append(dict(  planeIcao24 = loadedjson['planeIcao24'],
                        planeCallsign = loadedjson['planeCallsign'],
                        planeVelocity = loadedjson['planeVelocity'],
                        planeVerticalRate = loadedjson['planeVerticalRate'],
                        planeCountry = loadedjson['planeCountry'],
                        maxDecibels = loadedjson['maxDecibels'],
                        captureFormattedDate = loadedjson['captureFormattedDate'],
                        captureFormattedTime = loadedjson['captureFormattedTime'],
                        calculatedPlaneDistance = loadedjson['calculatedPlaneDistance'],
                        planeAlt = loadedjson['planeAlt']
                        ))
    return "lel" 

if __name__ == '__main__':
    app.run(debug=True, host = '0.0.0.0')





