CREATE TYPE bool_unk_enum AS ENUM ('true', 'false', 'unknown');
CREATE TYPE gen_enum AS ENUM ('male', 'female', 'other', 'unknown');
CREATE TYPE pregnancy_status_enum AS ENUM ('Pregnant', 'Delivered first child', 'Delivered second child', 'Twins', 'Miscarriage/ Still born', 'No pregnancy', 'unknown');
CREATE TYPE marital_status_enum AS ENUM ('Married', 'Single', 'Divorced', 'Separated', 'Widowed', 'unknown');
CREATE TYPE health_status_enum AS ENUM ('Deceased', 'Hospitalised for more than 5 days', 'In plaster at residence', 'Permanent disability as per disability certificate', 'None', 'unknown');
CREATE TYPE home_ownership_enum AS ENUM ('Home Owner', 'Tenant', 'Going to Purchase', 'unknown');
CREATE TYPE school_college_enum AS ENUM ('School', 'College', 'unknown');
