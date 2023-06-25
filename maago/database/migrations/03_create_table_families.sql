CREATE TABLE IF NOT EXISTS families (
    id VARCHAR(32),
    location_id VARCHAR(8),
    caste VARCHAR(64),
    caste_category VARCHAR(64),
    pr_of_cg bool_unk_enum,
    has_residence_certificate bool_unk_enum,
    ration_card_type VARCHAR(64),
    ptgo_or_pvtg bool_unk_enum,
    are_forest_dwellers bool_unk_enum,
    has_phone bool_unk_enum,
    has_neighbourhood_phone_number bool_unk_enum,    
    PRIMARY KEY (id),
    FOREIGN KEY (location_id) REFERENCES locations(id)
);