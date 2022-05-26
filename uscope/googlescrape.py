from datetime import datetime
from .models import PlaceGoogle, JobList, Place,  JobResults
from .db import db_session
from .helper import get_api_key, data_from_url, add_keyword_to_place, get_refresh_place_days
from time import sleep
from datetime import datetime, timedelta, date
import urllib.parse
from openlocationcode import openlocationcode
from sqlalchemy import func

apikey = get_api_key('googleapikey')
url = 'https://maps.googleapis.com/maps/api'
business_status_dict = {
    'OPERATIONAL': 1,
    'CLOSED_PERMANENTLY': 0,
    'CLOSED_TEMPORARILY': 2
}

def street_address_to_lat_lng(street_address):
    '''
    Converts a street address to a latitude/longitude dictionary
    input: string containing street address.
    output: dictionary of lat, lng
    '''

    urldir = "/place/findplacefromtext/json?&inputtype=textquery&fields=geometry&" + apikey
    latlongdict = {
        "lat": "",
        "lng": ""
    }

    urldir = urldir + "&input=" + urllib.parse.quote(street_address)
    data = data_from_url(url + urldir)
    if len(data['candidates']) == 0:
        raise Exception(
            "Error: street_address_to_lat_long: Couldn't find Address. " + urldir)
    if "error_message" in data:
        raise Exception(
            "Error: street_address_to_lat_long: error_message: " + data['error_message'])
    latlongdict['lat'] = data['candidates'][0]['geometry']['location']['lat']
    latlongdict['lng'] = data['candidates'][0]['geometry']['location']['lng']
    return latlongdict

def _make_street1(address_object):
    '''
    Turns an address object into a single "vicinity string"
    '''
    address_components = ['room', 'floor', 'street_number', 'route']
    address_dict = {}
    street1 = ''
    for address_component in address_components:
        for entry in address_object:
            if address_component in entry['types']:
                address_dict[address_component] = entry['short_name']
    if 'room' in address_dict:
        street1 += address_dict['room'] + '.'
    if 'floor' in address_dict:
        street1 += address_dict['floor'] + '/'
    if 'street_number' in address_dict:
        street1 += address_dict['street_number'] + " "
    if 'route' in address_dict:
        street1 += address_dict['route']
    return street1

def _get_address_component(address_object, componentname):
    return_value = ''
    for entry in address_object:
        if componentname in entry['types']:
            return_value = entry['short_name']
    return return_value


class google_search:
    googleidlist = []
    placeidlist = []
    location = dict()

    def __init__(self, location, radius, keyword=''):
        if type(location) is str:
            self.location = street_address_to_lat_lng(location)
        else:
            self.location = location
        self.googleidlist = []
        self.placeidlist = []
        self.nearby_search(radius, keyword)
                
    def nearby_search(self, radius, keyword=''):
        '''
        Finds a list of places nearby to the given location in the set radius.
        returns an array of google place ids
        '''
        #mylocation = street_address_to_lat_lng(self.location)
        urldir = '/place/nearbysearch/json?'
        urldir += apikey
        urldir += '&location=' + str(self.location['lat']) + ',' + str(self.location['lng'])
        urldir += '&radius=' + str(radius)
        if keyword != '':
            urldir += '&keyword=' + urllib.parse.quote(keyword)
        urldir += '&fields=place_id'
        data = data_from_url(url + urldir)
        if 'error_message' in data:
            raise Exception('Error: nearby_search: error message: ' + data['error_message'])
        if data['results'] is None:
            return
        for aresult in data['results']:
            if aresult['place_id'] not in self.googleidlist:
                self.googleidlist.append(aresult['place_id'])
        if 'next_page_token' in data:
            self.nearby_search_nextpage(data['next_page_token'])

        
    def nearby_search_nextpage(self, token, sleeptime=3):
        '''
        Gets a list of restaraunt from a next page token
        input: string containing token
        output: list of restaraunt dictionaries
        '''
        urldir = "&".join( ('/place/nearbysearch/json?pagetoken=' + token, apikey,))
        sleep(sleeptime)
        data = data_from_url(url + urldir)
        if 'error_message' in data:
            raise Exception('_nearby_search_nextpage: error_message: ' + data['error_message'])
        for aresult in data['results']:
            if aresult['place_id'] not in self.googleidlist:
                self.googleidlist.append(aresult['place_id'])
        if 'next_page_token' in data:
            self.nearby_search_nextpage(data['next_page_token'])
        
    def get_google_id_list(self):
        if self.googleidlist is None:
            return []
        return self.googleidlist

    def get_place_id_list(self, job_number=0):
        if len(self.placeidlist) > 0:
            return self.placeidlist
        for googleid in self.googleidlist:
            mygoogleplace = googleplace(googleid)
            mygoogleplace.get_googleplaceid()
            self.placeidlist.append(mygoogleplace.get_placeid())
            mygoogleplace.set_categories()
            mygoogleplace.set_jobnumber(job_number)
        myjob = JobList.query.filter(JobList.id == job_number).first()
        myjob.complete = True
        db_session.commit()
        return self.placeidlist

class googleplace:
    placeid = 0
    googleplaceid = 0
    myjson = dict()
    googleid = ""

    jobnumber = int()
    location = dict()
    googleplacerecord = PlaceGoogle()
    placerecord = Place()
    refresh = False

    def __init__(self, googleid, refresh=False):
        self.googleid = googleid
        self.refresh = refresh
        self.get_place_details()
        

    def get_place_details(self):
        self.googleplacerecord = PlaceGoogle.query.filter(PlaceGoogle.google_place_id == self.googleid).first()
        if (self.googleplacerecord is None) or self.refresh:
            self._get_json()
        self.get_placeid()
        if self.placerecord.lastchecked is None or self.placerecord.lastchecked < date.today() - timedelta(days = get_refresh_place_days()):
            self.refresh = True
            self._get_json()
        self.get_googleplaceid()

    def _get_json(self):
        fields = ['place_id', 'rating', 'address_component', 'business_status', 'geometry', 'name', 'type', 'vicinity', 'url', 'website','international_phone_number','user_ratings_total', 'plus_code']
        urldir = '/place/details/json?'
        urldir = urldir + apikey
        urldir = urldir + '&place_id='
        urldir = urldir + str(self.googleid)
        urldir = urldir + '&fields='
        urldir = urldir + ','.join(fields)
        fullurl = url + urldir
        self.myjson = data_from_url(fullurl)

    def get_googleplaceid(self):
        if (self.googleplaceid == 0) or (self.googleplaceid is None):
            self.googleplaceid = self.set_googleplaceid()
        return self.googleplaceid
    
    def set_googleplaceid(self):
        self.googleplacerecord = PlaceGoogle.query.filter(PlaceGoogle.google_place_id == self.googleid).first()
        if self.googleplacerecord is not None:
            self.googleplaceid = self.googleplacerecord.id
            if not self.refresh:
                return self.googleplacerecord.id
        if 'result' not in self.myjson:
            return 0
        aresult = self.myjson['result']
        if 'name' in aresult:
            name = aresult['name']
        if 'business_status' in aresult:
            business_status = business_status_dict[aresult['business_status']]
        else:
            business_status = 1
        lat = aresult['geometry']['location']['lat']
        lng = aresult['geometry']['location']['lng']
        rating = 0
        if 'rating' in aresult:
            rating = aresult['rating']
        user_ratings_total = 0
        if 'user_ratings_total' in aresult:
            user_ratings_total = aresult['user_ratings_total']
        placeurl = aresult['url']
        website = ''
        if 'website' in aresult:
            website = aresult['website']
        
        self.googleplacerecord = PlaceGoogle(placeid=self.placeid, business_status=business_status, lat=lat, lng=lng, rating=rating, user_ratings_total=user_ratings_total,
            google_place_id=self.googleid, mapurl=placeurl, website=website)
        db_session.add(self.googleplacerecord)
        db_session.commit()
        return self.googleplacerecord.id

    def get_placeid(self):
        if (self.placeid is not None) and (self.placeid > 0):
            return self.placeid
        if (self.googleplacerecord is None) or (self.googleplacerecord.placeid is None):
            self.set_placeid()
        if self.googleplacerecord is not None:
            self.placeid = self.googleplacerecord.placeid
            return self.placeid
        else:
            raise Exception('No place ID could be identified')

    def set_placeid(self, placeid=0):
        self.placerecord = Place.query.filter(Place.id == placeid).first()
        if self.placerecord is None:
            if self.myjson is None:
                self.get_place_details()
            if 'result' not in self.myjson: 
                raise Exception("No result in place id")
            aresult = self.myjson['result']
            name = aresult['name']
            address_components = aresult['address_components']
            street1 = _make_street1(address_components)
            suburb = _get_address_component(address_components, 'locality')
            restaurantstate = _get_address_component(address_components, 'administrative_area_level_1')
            postcode = _get_address_component(address_components, 'postal_code')
            vicinity = street1 + ', ' + suburb + ' ' + restaurantstate + ', ' + postcode
            phonenumber = '+61000000000'
            pluscode = self.get_pluscode()
            if 'international_phone_number' in aresult:
                phonenumber = aresult['international_phone_number'].replace(' ', '')
            self.placerecord = Place(placename=name, 
                placegoogleid=self.get_googleplaceid(), 
                street1=street1, suburb=suburb, 
                vicinity=vicinity, 
                postcode=postcode, 
                placestate=restaurantstate, 
                phonenumber=phonenumber,
                pluscode=pluscode,
                lastchecked=datetime.now())
            db_session.add(self.placerecord)
            db_session.commit()
            self.placeid = self.placerecord.id            
        else:
            self.placeid = placeid
        self.placerecord.placegoogleid = self.get_googleplaceid()
        if self.googleplaceid > 0:
            self.googleplacerecord.placeid = self.placeid
            db_session.commit()


    def set_categories(self):
        if self.myjson is None:
            self.get_place_details()
            types = self.myjson['result']['types']
            for mytype in types:
                add_keyword_to_place(self.get_placeid(), mytype)

    

    def get_placename(self):
        return self.placerecord.placename

    def set_yelpplace(self, yelpplaceid):
        self.placerecord.yelpplaceid = yelpplaceid

    def set_jobnumber(self, jobnumber):
        if self.get_placeid() == 0:
            return
        db_session.add(JobResults(placeid=self.get_placeid(), joblistid=jobnumber))
        db_session.commit()

    def get_location(self):
        if self.googleplacerecord is None:
            aresult = self.myjson['result']
            lat = aresult['geometry']['location']['lat']
            lng = aresult['geometry']['location']['lng']
            location = dict(lat = lat,
                lng = lng)
        else:
            location = dict(lat = self.googleplacerecord.lat,
                lng = self.googleplacerecord.lng)
        return location
    
    def get_pluscode(self):
        mylocation = self.get_location()
        return openlocationcode.encode(mylocation['lat'], mylocation['lng'])
        
    


