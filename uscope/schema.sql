DROP TABLE IF EXISTS configkeys;
DROP TABLE IF EXISTS place;
DROP TABLE IF EXISTS placegoogle;
DROP TABLE IF EXISTS keywords;
DROP TABLE IF EXISTS joblist;
DROP TABLE IF EXISTS jobresults;

CREATE TABLE configkeys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyname TEXT UNIQUE NOT NULL,
    keyvalue TEXT NOT NULL
);

CREATE TABLE place (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    placename TEXT,
    placegoogleid INTEGER NOT NULL,
    vicinity TEXT,
    street1 TEXT,
    street2 TEXT,
    suburb TEXT,
    postcode TEXT,
    placestate TEXT,
    phonenumber TEXT,
    pluscode TEXT,
    FOREIGN KEY (placegoogleid)
        REFERENCES placegoogle (id)
            ON DELETE CASCADE
);

CREATE TABLE placegoogle (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    placeid INTEGER NOT NULL,
    business_status INTEGER,
    lat FLOAT,
    lng FLOAT,
    rating FLOAT,
    user_ratings_total INTEGER,
    google_place_id TEXT,
    mapurl TEXT,
    website TEXT,
    FOREIGN KEY (placeid)
        REFERENCES place (id)
);

CREATE TABLE keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    placeid INTEGER NOT NULL,
    keyword TEXT,
    FOREIGN KEY (placeid)
        REFERENCES place (id)
);

CREATE TABLE joblist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pointaddress TEXT,
    radius INTEGER,
    lat FLOAT,
    lng FLOAT,
    searchterms TEXT,
    placecount INTEGER,
    complete INTEGER
);

CREATE TABLE jobresults (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    placeid INTEGER,
    joblistid INTEGER,
    FOREIGN KEY (placeid)
        REFERENCES place (id)
    FOREIGN KEY (joblistid)
        REFERENCES joblist (id)
);