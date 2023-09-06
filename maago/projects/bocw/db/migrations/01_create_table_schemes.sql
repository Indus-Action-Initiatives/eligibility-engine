CREATE TABLE IF NOT EXISTS schemes (
    id VARCHAR(8),
    name VARCHAR(256),
    -- right VARCHAR(128),
    state VARCHAR(64),
    inclusion_criteria VARCHAR(1024),
    exclusion_criteria VARCHAR(1024),
    PRIMARY KEY (id)
);