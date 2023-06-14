CREATE TABLE scheme_beneficiaries (
    scheme_id VARCHAR(8),
    beneficiary_id VARCHAR(8),
    number_of_times_availed TINYINT,
    FOREIGN KEY (scheme_id) REFERENCES schemes(id),
    FOREIGN KEY (beneficiary_id) REFERENCES family_members(id)
);
