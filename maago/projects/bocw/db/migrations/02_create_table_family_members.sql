CREATE TABLE IF NOT EXISTS family_members (
    id VARCHAR(8),
    bocw_card_registration_date DATE NULL DEFAULT NULL,
    gender gen_enum,
    pregnancy_status pregnancy_status_enum,
    age FLOAT,
    occupation VARCHAR(256),
    marital_status marital_status_enum,
    health_status health_status_enum,    
    number_of_children INT,
    children_married marital_status_enum,
    children_school_or_college school_college_enum,
    spouse_alive bool_unk_enum,
    occupation_of_surviving_spouse VARCHAR(256),
    receiving_pension bool_unk_enum,
    receiving_government_aid bool_unk_enum,
    home_ownership_status home_ownership_enum,
    PRIMARY KEY (id)
);
