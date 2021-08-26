import os
import requests
from math import sin, cos, sqrt, atan2, radians

GOOGLE_API = 'AIzaSyAroJaCwY6-fz65M4n5WG2U8mYL0McmeGc'
URL = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&' \
      'origins=%s&destinations=%s&key=%s'

URL_LATLNG = "https://maps.googleapis.com/maps/api/geocode/json?latlng=%s&key=%s"
URL_ADDRESS = "https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s"

def get_distance(location_1, location_2):

    R = 6373.0

    lat1 = radians(float(location_1['latitude']))
    lon1 = radians(float(location_1['longitude']))
    lat2 = radians(float(location_2['latitude']))
    lon2 = radians(float(location_2['longitude']))

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    return distance / 1.609


def fetch_data(origin, destinations):
    response = requests.get(URL % (origin, destinations, GOOGLE_API))
    return response


def get_eta(origin, destinations):
    data = fetch_data(origin, destinations)
    if check_status(data):
        return data['elements'][0]['duration']['value']
    return False


def check_status(status):
    return status == 'OK'


def prepare_origin(origin):
    return origin['longitude']+','+origin['latitude']


def prepare_destination(destination):
    supplier_string = ''
    for supplier in destination:
        supplier_string = supplier_string + supplier['location']['longitude'] + ',' + supplier['location'][
            'latitude'] + '|'

    return supplier_string[:-1]


def get_address(lat, lon):
    location = f"{lat},{lon}"
    response = requests.get(URL_LATLNG % (location, GOOGLE_API))
    data = response.json()
    if data['status'] == 'OK':
        return data['results'][0]['formatted_address']

    return ''

def get_by_address(address):
    location = f"{address}"
    response = requests.get(URL_ADDRESS % (location, GOOGLE_API))
    data = response.json()
    if data['status'] == 'OK':
        return data['results'][0]['geometry']['location']

    return ''
