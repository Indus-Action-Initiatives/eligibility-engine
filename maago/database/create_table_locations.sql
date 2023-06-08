CREATE TABLE locations (
    id VARCHAR(8),
    location_type ENUM('rural', 'urban'),
    locality VARCHAR(256),
    pincode INT,
    ward_number SMALLINT,
    ward_name VARCHAR(256),
    village VARCHAR(256),
    survey_village_town_city VARCHAR(256),
    PRIMARY KEY (id)
);