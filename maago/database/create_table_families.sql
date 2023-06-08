CREATE TABLE families (
    id VARCHAR(8),
    location_id VARCHAR(8),
    caste VARCHAR(64),
    caste_category VARCHAR(64),
    pr_of_cg ENUM('true', 'false', 'unknown'),
    has_residence_certificate ENUM('true', 'false', 'unknown'),
    ration_card_type VARCHAR(64),
    ptgo_or_pvtg ENUM('true', 'false', 'unknown'),
    are_forest_dwellers ENUM('true', 'false', 'unknown'),
    has_phone ENUM('true', 'false', 'unknown'),
    has_neighbourhood_phone_number ENUM('true', 'false', 'unknown'),    
    PRIMARY KEY (id),
    FOREIGN KEY (location_id) REFERENCES locations(id)
);