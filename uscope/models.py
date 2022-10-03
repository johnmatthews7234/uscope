from sqlalchemy import Column, ForeignKey, Integer, String, Float, Boolean, Date, DateTime, table
from sqlalchemy import Table, MetaData, inspect
from sqlalchemy.orm import declarative_base, relationship
from flask_user import UserMixin
from .db import Base, engine


class ConfigKeys(Base):
    __tablename__ = "configkeys"

    id = Column('id', Integer, primary_key=True)
    keyname = Column('keyname', String)
    keyvalue = Column('keyvalue', String)

    def __init__(self, keyname = None, keyvalue= None):
        self.keyname = keyname
        self.keyvalue = keyvalue

    def create_table(self):
        table = Table(self.__tablename__, ConfigKeys.id, ConfigKeys.keyname, ConfigKeys.keyvalue)
        table.create(engine)

class Place(Base):
    __tablename__ = "place"

    id = Column('id', Integer, primary_key=True)
    placename = Column('placename', String)
    placegoogleid = Column('placegoogleid', Integer, ForeignKey('placegoogle.id', ondelete='CASCADE'))
    vicinity = Column('vicinity', String)
    street1 = Column('street1', String)
    street2 = Column('street2', String)
    suburb = Column('suburb', String)
    postcode = Column('postcode', String)
    placestate = Column('placestate', String)
    phonenumber = Column('phonenumber', String)
    pluscode = Column('pluscode', String)
    lastchecked = Column('lastchecked', Date)
    
    def __init__(self, placename=None, placegoogleid=None, vicinity=None, street1=None, street2=None, suburb=None, postcode=None,
        placestate=None, phonenumber=None, pluscode=None, lastchecked=None):
        
        self.placename = placename
        self.placegoogleid = placegoogleid
        self.vicinity = vicinity
        self.street1 = street1
        self.street2 = street2
        self.suburb = suburb
        self.postcode = postcode
        self.placestate = placestate
        self.phonenumber = phonenumber
        self.pluscode = pluscode
        self.lastchecked = lastchecked
        
    def create_table(self):
        table = Table(self.__tablename__, self.id, self.placename, self.placegoogleid, self.vicinity,
               self.street1, self.street2, self.suburb, self.postcode, self.placestate, self.phonenumber,
               self.pluscode, self.lastchecked)
        table.create(engine)

class PlaceGoogle(Base):
    __tablename__ = "placegoogle"

    id = Column('id', Integer, primary_key=True)
    placeid = Column('placeid', Integer, ForeignKey('place.id'))
    business_status = Column('business_status', Integer)
    lat = Column('lat', Float)
    lng = Column('lng', Float)
    rating = Column('rating', Float)
    user_ratings_total = Column('user_ratings_total', Integer)
    google_place_id = Column('google_place_id', String)
    mapurl = Column(String)
    website = Column(String)

    def __init__(self, placeid=None, business_status=None, lat=None, lng=None, rating=None, user_ratings_total=None,
        google_place_id=None, mapurl=None, website=None):

        self.placeid = placeid
        self.business_status = business_status
        self.lat = lat
        self.lng = lng
        self.rating = rating
        self.user_ratings_total = user_ratings_total
        self.google_place_id = google_place_id
        self.mapurl = mapurl
        self.website = website

    def create_table(self):
        table = Table(self.__tablename__, self.id, self.placeid, self.business_status, self.lat, self.lng, self.rating,
            self.user_ratings_total, self.google_place_id, self.mapurl, self.website )
        table.create(engine)

class KeyWords(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True)
    placeid = Column(Integer, ForeignKey('place.id', ondelete='CASCADE'))
    keyword = Column(String)

    def __init__(self, placeid=None, keyword=None):
        self.placeid = placeid
        self.keyword = keyword

    def create_table(self):
        table = Table(self.__tablename__, self.id, self.placeid, self.keyword)
        table.create(engine)

class JobList(Base):
    __tablename__ = "joblist"

    id = Column(Integer, primary_key=True)
    pointaddress = Column(String)
    radius = Column(Integer)
    lat = Column(Float)
    lng = Column(Float)
    searchterms = Column(String)
    placecount = Column(Integer)
    complete = Column(Boolean)

    def __init__(self, pointaddress=None, radius=None, lat=None, lng=None, searchterms=None, placecount=None, complete=None):
        self.pointaddress = pointaddress
        self.radius = radius
        self.lat = lat
        self.lng = lng
        self.searchterms = searchterms
        self.placecount = placecount
        self.complete = complete
    
    def create_table(self):
        table = Table(self.__tablename__, self.id, self.pointaddress, self.radius, self.lat, self.lng, self.searchterms, self.placecount, self.complete)
        table.create(engine)

class JobResults(Base):
    __tablename__ = "jobresults"

    id = Column(Integer, primary_key=True)
    placeid = Column(Integer, ForeignKey('place.id'))
    joblistid = Column(Integer, ForeignKey('joblist.id'))

    def __init__(self, placeid=None, joblistid=None):
        self.placeid = placeid
        self.joblistid = joblistid

    def create_table(self):
        table = Table(self.__tablename__, self.id, self.placeid, self.joblistid)
        table.create(engine)

class User(Base, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    active = Column('is_active', Boolean, nullable=False, server_default='1')
    email = Column(String(255, collation='NOCASE'), nullable=False, unique=True)
    email_confirmed_at = Column(DateTime())
    password = Column(String(255), nullable=False, server_default='')
    first_name = Column(String(100, collation='NOCASE'), nullable=False, server_default='')
    last_name = Column(String(100, collation='NOCASE'), nullable=False, server_default='')
    roles = relationship('Role', secondary='user_roles')

    def create_table(self):
        table = Table(self.__tablename__, self.id, self.active, self.email, self.email_confirmed_at, self.password, self.first_name, self.last_name, self.roles)
        table.create(engine)

class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer(), primary_key=True)
    name = Column(String(50), unique=True)

    def create_table(self):
        table = Table(self.__tablename__, self.id, self.name)
        table.create(engine)

class UserRoles(Base):
    __tablename__ = 'user_roles'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    role_id = Column(Integer, ForeignKey('roles.id', ondelete='CASCADE'))

    def create_table(self):
        table = Table(self.__tablename__, self.id, self.user_id, self.role_id)
        table.create(engine)


class LinkedInTokens(Base):
    __tablename__ = 'linkedin_tokens'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    token = Column(String(1000))
    expires = Column(DateTime())
    username = Column(String(255))
    password = Column(String(100))

    def __init__(self, user_id, token=None, expires=None, username=None, password=None):
        self.user_id = user_id
        self.token = token
        self.expires = expires
        self.username = username
        self.password = password

    def create_table(self):
        table = Table(self.__tablename__, self.id, self.user_id, self.token, self.expires, self.username, self.password)
        table.create(engine)


 
