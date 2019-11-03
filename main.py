'''
    test:10:00 11-10-2019
'''
import datetime
import json
import math
import os
import signal
import subprocess
import sys
import time
import traceback
from collections import deque

import requests
from geopy.geocoders import Nominatim

import ws1361
from opensky_api import OpenSkyApi

    # pylint: disable=broad-except

class EntityToWrite():
    '''
    An object that when serialized fits into roelofs database call
    '''
    # pylint: disable=invalid-name
    # towrite = EntityToWrite()
    partitionkey = None
    rowkey = None
    def __init__(self, myLat, myLng, myAlt, valueArray, state, distance, settings):
        '''
        :param myLat
        Constructor of EntityToWrite
        '''
        x = datetime.datetime.now()
        self.captureTimestamp = round(time.time())
        self.captureType = "automatic"
        self.captureFormattedDate = x.strftime("%Y")+x.strftime("%m")+x.strftime("%d")
        self.captureFormattedTime = x.strftime("%X")
        self.maxDecibels = round(max(valueArray))
        self.decibelsArray = list(valueArray)
        self.averageSampleRollupDurationInMs = 1000
        self.sampleDurationInMs = 13000
        self.myLat = round(myLat, 2)
        self.myLng = round(myLng, 2)
        self.myAlt = myAlt
        self.deviceCordova = ""
        self.deviceModel = settings["model"]
        self.devicePlatform = settings["platform"]
        self.deviceVersion = settings["rpiversion"]
        self.deviceManufacturer = "Raspberry pi"
        self.deviceIsVirtual = False
        self.deviceSerial = get_mac(get_eth_name())
        self.planeIcao24 = state.icao24
        self.planeCallsign = state.callsign
        self.planeCountry = state.origin_country
        self.planeLat = state.latitude
        self.planeLng = state.longitude
        self.planeAlt = state.geo_altitude
        self.planeTimePosition = state.time_position
        self.planeOnGround = state.on_ground
        self.planeVelocity = state.velocity
        self.planeTrueTrack = state.heading
        self.planeVerticalRate = state.vertical_rate
        self.planeSquawk = state.squawk
        self.planeSpi = state.spi
        self.planePositionSource = state.position_source
        self.calculatedPlaneDistance = distance
        self.appVersion = "1.00 PI Test"

def get_eth_name():
    '''
    Get name of the Ethernet interface
    '''
    #pylint: disable=unused-variable
    try:
        for root, dirs, files in os.walk('/sys/class/net'):
            for val in dirs:
                if val[:3] == 'enx' or val[:3] == 'eth':
                    interface = val
    except Exception as exept:
        print(exept)
        print(traceback.format_exc())

        interface = "None"
    return interface

def get_mac(interface):
    '''
    Return the MAC address of the specified interface
    '''
    try:
        val = open('/sys/class/net/{0}/address'.format(interface)).read()
    except Exception as exept:
        print(exept)
        print(traceback.format_exc())
        val = "00:00:00:00:00:00"
    return val[0:17]

def write_to_database(towrite, settings):
    '''
    Writes to our and roelofs database
    '''
    response = requests.get(settings["apilink"])
    loadedresponse = json.loads(response.content)

    for i in loadedresponse:
        if i["RowKey"] == "RegisterFunction":
            rowkey = i["RowKey"]
            api = i["Value"]
            partitionkey = i["PartitionKey"]

    api2 = "http://127.0.0.1:5000/submit"

    towrite.partitionkey = partitionkey
    towrite.rowkey = rowkey
    towritejson = json.dumps(towrite.__dict__)
    headers = {'Content-type': 'application/json'}
    requests.post(api, data=towritejson, headers=headers)
    requests.post(api2, data=towritejson, headers=headers)


    return towrite

def get_endpoint(lat1, lon1, bearing, distance):
    '''
    Takes a point in decimal latlong a breaing and a distance
    Returns a latlong in the direction and distance specified
    https://stackoverflow.com/questions/33001420/find-destination-coordinates-given-starting-coordinates-bearing-and-distance#33026930
    '''
    radius = 6371                #Radius of the Earth
    brng = math.radians(bearing) #convert degrees to radians
    distance = distance*1.852                  #convert nautical miles to km
    lat1 = math.radians(lat1)    #Current lat point converted to radians
    lon1 = math.radians(lon1)    #Current long point converted to radians
    lat2 = math.asin(math.sin(lat1)*math.cos(distance/radius)
                     + math.cos(lat1)*math.sin(distance/radius)*math.cos(brng))
    lon2 = lon1 + math.atan2(math.sin(brng)*math.sin(distance/radius)*math.cos(lat1)
                             , math.cos(distance/radius)-math.sin(lat1)*math.sin(lat2))
    lat2 = math.degrees(lat2)
    lon2 = math.degrees(lon2)
    return lat2, lon2

def print_plane(state):
    '''
    Print a plane to the terminal
    '''
    print("({}, {} {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {})"
          .format(state.icao24, state.callsign, state.origin_country, state.latitude
                  , state.longitude, state.baro_altitude, state.time_position, state.on_ground
                  , state.velocity, state.heading, state.vertical_rate, state.squawk, state.spi
                  , state.position_source))

def haversine(lat1, lon1, lat2, lon2):
    '''
    Returns the distance between
    https://janakiev.com/blog/gps-points-distance-python/
    '''
    radius = 6372800  # Earth radius in meters

    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a_a = math.sin(dphi/2)**2 + \
        math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2

    return 2*radius*math.atan2(math.sqrt(a_a), math.sqrt(1 - a_a))

def get_distance(location, state, altitude):
    '''
    Returns distance between us and the plane
    '''
    ground = haversine(location.latitude, location.longitude, state.latitude, state.longitude)
    heigtdiff = state.geo_altitude - altitude
    csquared = pow(ground, 2)+pow(heigtdiff, 2)
    val = math.sqrt(csquared)
    return val

def gm1356handler(signum, frame):
    '''
    Exception for if the gm1356
    '''
    print("gm1356 is not responding")
    raise Exception("timeout exception")

def read_gm1356(valuequeue, gm1356path):
    '''
    Read values from gm1356
    '''
    averagevalue = 0
    try:
        signal.alarm(2)
        gm1356 = int(round(float(subprocess.check_output([gm1356path])), 1))
        valuequeue.pop()
        valuequeue.appendleft(gm1356)
        averagevalue = sum(valuequeue)/float(len(valuequeue))
        signal.alarm(0)
        return gm1356, valuequeue, averagevalue
    except Exception as exept:
        print(exept)
        print(traceback.format_exc())
        gm1356, valuequeue, averagevalue = read_gm1356(valuequeue, gm1356path)
        return gm1356, valuequeue, averagevalue

def read_ws1361(device):
    #TODO this can probe be removed
    '''
    reads
    '''
    decibels, measurerange, weight, speed = ws1361.readSPL(device)
    return round(decibels, 1), measurerange, weight, speed

def call_opensky_api(lowerboundlat, upperboundlat, lowerboundlong, upperboundlong):
    '''
    Call the opensky api return states if there are any else return empty list
    '''
    try:
        api = OpenSkyApi()
        #min_latitude, max_latitude, min_longitude, max_longitude
        states = api.get_states(bbox=(lowerboundlat, upperboundlat, lowerboundlong, upperboundlong))
        if len(states.states) >= 1:
            return states.states
        #else
        emptystatestring = []
        print("No planes in range")
        return emptystatestring

    except Exception as exept:
        print("Opensky api call broke: {0}".format(exept))
        print(sys.exc_info()[0])
        print(traceback.format_exc())
        emptystatestring = []
        return emptystatestring

def read_settings():
    '''
    Returns a dict of settings
    '''
    with open('settings.json') as settingsjsonfile:
        settings = json.load(settingsjsonfile)
    return settings

def update_settings():
    '''
    Updates the setting and writes them to json
    '''
    try:
        with open('usersettings.json') as usersettingsjsonfile:
            usersettings = json.load(usersettingsjsonfile)
        os.remove('usersettings.json')
    except Exception as exept:
        print(traceback.format_exc())
        usersettings = False
        print(exept)

    settings = read_settings()
    version = subprocess.run(["./getdeviceversion.sh"]
                             , capture_output=True, encoding='utf-8', check=True)
    model = subprocess.run(["./getdevicemodel.sh"]
                           , capture_output=True, encoding='utf-8', check=True)
    platform = subprocess.run(["./getdeviceplatform.sh"]
                              , capture_output=True, encoding='utf-8', check=True)

    settings["rpiversion"] = version.stdout.rstrip('\n\x00')
    settings["model"] = model.stdout.rstrip('\n\x00')
    settings["platform"] = platform.stdout.rstrip('\n\x00')

    if usersettings is not False:
        settings["threshold"] = usersettings["threshold"]
        settings["location"] = usersettings["location"]
        settings["samplesize"] = usersettings["samplesize"]
        settings["cutoffheight"] = usersettings["cutoffheight"]
        settings["altitude"] = usersettings["altitude"]

    with open('settings.json', 'w') as file:
        json.dump(settings, file)

def main():
    '''
    Main
    '''
    mic = "ws1361"

    startingarray = [30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30]
    valuequeue = deque(startingarray)
    averagevalue = 0
    lastplane = ""
    lasttime = time.time()
    signal.signal(signal.SIGALRM, gm1356handler)
    update_settings()
    settings = read_settings()
    locationsetting = settings["location"]
    altitude = settings["altitude"]
    radius = settings["radius"]
    gm1356path = settings["gm1356path"]
    if mic == "ws1361":
        device = ws1361.connect()
    threshold = settings["threshold"]
    samplesize = settings["samplesize"]
    counter = 0

    geolocator = Nominatim(user_agent="RPIAirplanecounter")
    # TODO specific user agent for notanim
    location = geolocator.geocode(locationsetting)
    
    print(location.raw)

    upperboundlat, lowerboundlong = get_endpoint(location.latitude, location.longitude, 315, radius)
    lowerboundlat, upperboundlong = get_endpoint(location.latitude, location.longitude, 135, radius)

    print("upperbound {0}, {1}, lowerbound {2}, {3}"
          .format(upperboundlat, upperboundlong, lowerboundlat, lowerboundlong))

    print('Initialization complete')

    while True:
        #pylint: disable=unused-variable
        if mic == "gm1356":
            currentval, valuequeue, averagevalue = read_gm1356(valuequeue, gm1356path)

        if mic == "ws1361":
            currentval, measurerange, weight, speed = ws1361.readSPL(device)
            valuequeue.pop()
            valuequeue.appendleft(round(currentval, 1))
            averagevalue = sum(valuequeue)/float(len(valuequeue))

        averagevalue = round(averagevalue, 1)
        base = '{:%Y-%m-%d %H:%M:%S}: {} Average: {}'

        print(base.format(datetime.datetime.now(), round(currentval, 1), averagevalue))

        if (currentval >= threshold) & ((time.time()-lasttime) >= 20):
            counter = counter+1
            print("counter = ", counter)
            if counter >= samplesize:
                states = call_opensky_api(lowerboundlat, upperboundlat
                                          , lowerboundlong, upperboundlong)
                try:
                    if len(states) >= 1:
                        for state in states:
                            if state.icao24 != lastplane:
                                lastplane = state.icao24
                                lasttime = time.time()
                                distance = 0
                                print_plane(state)
                                if state.latitude is not None and state.longitude is not None and state.geo_altitude is not None:
                                    distance = round(get_distance(location, state, altitude))
                                    print("distance = ", distance)

                                    towrite = EntityToWrite(location.latitude, location.longitude, altitude, valuequeue, state, distance, settings)
                                    writeattempt = write_to_database(towrite, settings)
                                    print(json.dumps(writeattempt.__dict__))
                                    #TODO implement cutoffheight

                except Exception as exept:
                    print(exept)
                    print(sys.exc_info()[0])
                    print(traceback.format_exc())

                counter = 0

        else:
            counter = 0

        time.sleep(1)

main()
