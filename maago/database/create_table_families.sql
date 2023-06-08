CREATE TABLE families (
    id VARCHAR(8),
    location_id VARCHAR(8),
    caste VARCHAR(64),
    caste_category VARCHAR(64),
    pr_of_cg boolean,
    has_residence_certificate boolean,
    ration_card_type VARCHAR(64),
    ptgo_or_pvtg boolean,
    are_forest_dwellers boolean,
    has_phone boolean,
    has_neighbourhood_phone_number boolean,    
    PRIMARY KEY (id),
    FOREIGN KEY (location_id) REFERENCES locations(id)
);