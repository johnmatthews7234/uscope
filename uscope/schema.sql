--
-- File generated with SQLiteStudio v3.3.3 on Mon Jun 20 17:14:07 2022
--
-- Text encoding used: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: configkeys
DROP TABLE IF EXISTS configkeys;

CREATE TABLE configkeys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyname TEXT UNIQUE NOT NULL,
    keyvalue TEXT NOT NULL
);


-- Table: joblist
DROP TABLE IF EXISTS joblist;

CREATE TABLE joblist (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    pointaddress TEXT,
    radius       INTEGER,
    lat          FLOAT,
    lng          FLOAT,
    searchterms  TEXT,
    placecount   INTEGER,
    complete     BOOLEAN DEFAULT (False) 
);


-- Table: jobresults
DROP TABLE IF EXISTS jobresults;

CREATE TABLE jobresults (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    placeid   INTEGER,
    joblistid INTEGER,
    FOREIGN KEY (
        placeid
    )
    REFERENCES place (id),
    FOREIGN KEY (
        joblistid
    )
    REFERENCES joblist (id) 
);


-- Table: keywords
DROP TABLE IF EXISTS keywords;

CREATE TABLE keywords (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    placeid INTEGER NOT NULL,
    keyword TEXT,
    FOREIGN KEY (
        placeid
    )
    REFERENCES place (id) 
);


-- Table: place
DROP TABLE IF EXISTS place;

CREATE TABLE place (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    placename     TEXT,
    placegoogleid INTEGER NOT NULL,
    vicinity      TEXT,
    street1       TEXT,
    street2       TEXT,
    suburb        TEXT,
    postcode      TEXT,
    placestate    TEXT,
    phonenumber   TEXT,
    pluscode      TEXT,
    lastchecked   INTEGER,
    FOREIGN KEY (
        placegoogleid
    )
    REFERENCES placegoogle (id) ON DELETE CASCADE
);


-- Table: placegoogle
DROP TABLE IF EXISTS placegoogle;

CREATE TABLE placegoogle (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    placeid            INTEGER NOT NULL,
    business_status    INTEGER,
    lat                FLOAT,
    lng                FLOAT,
    rating             FLOAT,
    user_ratings_total INTEGER,
    google_place_id    TEXT,
    mapurl             TEXT,
    website            TEXT,
    FOREIGN KEY (
        placeid
    )
    REFERENCES place (id) 
);

-- Table: roles
DROP TABLE IF EXISTS roles;

CREATE TABLE "roles" (
	"id"	INTEGER,
	"name"	TEXT UNIQUE,
	PRIMARY KEY("id")
);


-- Table: user_roles
DROP TABLE IF EXISTS user_roles;

CREATE TABLE "user_roles" (
	"id"	INTEGER,
	"user_id"	INTEGER,
	"role_id"	INTEGER,
	FOREIGN KEY("user_id") REFERENCES "users"("id") ON DELETE CASCADE,
	FOREIGN KEY("role_id") REFERENCES "roles"("id") ON DELETE CASCADE,
	PRIMARY KEY("id")
);


-- Table: users
DROP TABLE IF EXISTS users;

CREATE TABLE "users" (
	"id"	INTEGER,
	"email"	TEXT NOT NULL UNIQUE,
	"email_confirmed_at"	INTEGER,
	"username"	TEXT NOT NULL UNIQUE,
	"password"	TEXT NOT NULL,
	"active"	INTEGER,
	"first_name"	TEXT NOT NULL,
	"last_name"	TEXT NOT NULL,
	PRIMARY KEY("id")
);

CREATE TABLE "user_emails" (
	"id"	INTEGER,
	"user_id"	INTEGER,
	"email"	TEXT NOT NULL UNIQUE,
	"email_confirmed_at"	INTEGER,
	"is_primary"	INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY("id")
);
COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
