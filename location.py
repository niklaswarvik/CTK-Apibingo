import math
import numpy as np
import posConvert as pc
import requests

def distanceStraight(loc1, loc2):
    return math.sqrt(math.pow(loc1[0]-loc2[0],2) + math.pow(loc1[1]-loc[2],2))

def distanceRound(loc1, loc2):

    R = 6371000;
    dLat = math.toRadians(loc2[0]-loc1[0])
    dLon = math.toRadians(loc2[1]-loc1[1])
    lat1 = loc1[0]
    lat2 = loc2[0]

    a = Math.sin(dLat/2) * Math.sin(dLat/2) + Math.sin(dLon/2) * Math.sin(dLon/2) * Math.cos(lat1) * Math.cos(lat2)

    c = 2 * Math.atan2(Math.sqrt(a), math.sqrt(1-a))

    d = R * c

    return d

    #var R = 6371; // km
    #var dLat = (lat2-lat1).toRad();
    #var dLon = (lon2-lon1).toRad();
    #var lat1 = lat1.toRad();
    #var lat2 = lat2.toRad();
    #
    #var a = Math.sin(dLat/2) * Math.sin(dLat/2) +
    #        Math.sin(dLon/2) * Math.sin(dLon/2) * Math.cos(lat1) * Math.cos(lat2); 
    #var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)); 
    #var d = R * c;

def rt90_to_wgs84(loc):
    pc.rt90_to_wgs84(loc[0], loc[1])

def wgs84_to_rt90(loc):
    pc.wgs84_to_rt90(loc[0], loc[1])

def getAddressLocation(address):
    url = 'http://maps.googleapis.com/maps/api/geocode/json'
    params = dict(address=address)

    resp = requests.get(url=url, params=params)
    data = resp.json()
    result = [];
    for i in range(0,len(data["results"])):
    	print(i)
    	result.append((data["results"][0]["formatted_address"], data["results"][0]["geometry"]["location"]))
    return result

