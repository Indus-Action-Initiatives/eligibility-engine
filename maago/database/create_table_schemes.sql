CREATE TABLE schemes (
    id VARCHAR(8),
    name VARCHAR(256),
    state VARCHAR(64),
    department VARCHAR(32),
    scheme VARCHAR(256),
    description VARCHAR(1024),
    inclusion_criteria VARCHAR(1024),
    exclusion_criteria VARCHAR(1024),
    PRIMARY KEY (id)
);