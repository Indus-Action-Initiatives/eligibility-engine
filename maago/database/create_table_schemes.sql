CREATE TABLE schemes (
    id VARCHAR(8),
    name VARCHAR(256),
    right VARCHAR(128),
    state VARCHAR(64),
    department VARCHAR(32),
    description VARCHAR(1024),
    inclusion_criteria VARCHAR(1024),
    exclusion_criteria VARCHAR(1024),
    PRIMARY KEY (id)
);