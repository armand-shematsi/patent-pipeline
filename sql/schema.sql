-- Global Patent Intelligence Database Schema
-- Created for PatentsView Data Pipeline Project

CREATE TABLE IF NOT EXISTS patents (
    patent_id   TEXT PRIMARY KEY,
    title       TEXT,
    abstract    TEXT,
    filing_date TEXT,
    year        INTEGER
);

CREATE TABLE IF NOT EXISTS inventors (
    inventor_id TEXT,
    name        TEXT,
    city        TEXT,
    state       TEXT,
    country     TEXT,
    patent_id   TEXT
);

CREATE TABLE IF NOT EXISTS companies (
    company_id  TEXT,
    name        TEXT,
    city        TEXT,
    state       TEXT,
    country     TEXT,
    patent_id   TEXT
);

CREATE TABLE IF NOT EXISTS locations (
    location_id TEXT PRIMARY KEY,
    city        TEXT,
    state       TEXT,
    country     TEXT,
    latitude    REAL,
    longitude   REAL
);

CREATE TABLE IF NOT EXISTS relationships (
    patent_id   TEXT,
    inventor_id TEXT,
    company_id  TEXT
);
