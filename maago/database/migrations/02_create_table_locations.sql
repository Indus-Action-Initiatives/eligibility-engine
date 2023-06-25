CREATE TABLE IF NOT EXISTS locations (
    id VARCHAR(8),
    location_type loc_typ_enum,
    locality VARCHAR(256),
    pincode INT,
    ward_number SMALLINT,
    ward_name VARCHAR(256),
    village VARCHAR(256),
    survey_village_town_city VARCHAR(256),
    PRIMARY KEY (id)
);