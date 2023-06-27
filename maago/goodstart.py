#!/usr/bin/env python
#
# Angshuman Guha
# angshuman.guha@gmail.com

import sys
from loaders.beneficiary_scheme_mapping import GetBeneficiarySchemesMapping
from loaders.beneficiary_loaders import LoadBeneficiariesFromFile
import csv
from utils.proximity_score import InitGlobals

entities = {
    "id": [],
    "family": [],
    "respondent": [],
    "familyMember": [],
}


def getEntityForHeader(header):
    entity = "family"
    for k, v in entities.items():
        if header in v:
            entity = k
            break
    return entity


"""
        type Location struct {
            areaType: string;
            areaLocality: string;
            pincode: string;
            wardNumber: int;
            wardName: string;
            village: string;
            surveyVillageTownCity: string;
        }

        type FamilyMember struct {
            name: string;
            dob: date;
            gender: string;
            familyRole: string;
            disadvantaged: bool;
            pregnancy: bool;
            job: string;
            jobType: string;
            inEducationalInstitute: bool;
            educationLevel: string;
            prevYearTenth: bool;
            prevYearTwelfth: bool;
            tenthPercentageMarks: float;
            twelfthPercentageMarks: float;
            tenthTopTen: bool;
            twelfthTopTen: bool;
            hasBOCWCard: bool;
            bocwCardIssueDate: date;
            hasUOWCard: bool;
            uowCardIssueDate: date;
        }

        type Family struct {
            id: string;
            caste: string;
            casteCategory: string;
            PRofCG: bool;
            hasResidenceCertificate: bool;
            rationCardType: string;
            ptgoOrPVTG: bool;
            areForestDwellers: bool;
            hasPhone: bool;
            hasNeighbourPhoneNumber: bool;
            location: Location;
            members: []FamilyMember;
        }

        +--------------------------------+--------------------------------+------+-----+---------+-------+
| Field                          | Type                           | Null | Key | Default | Extra |
+--------------------------------+--------------------------------+------+-----+---------+-------+
| id                             | varchar(32)                    | NO   | PRI | NULL    |       |
| location_id                    | varchar(8)                     | YES  | MUL | NULL    |       |
| caste                          | varchar(64)                    | YES  |     | NULL    |       |
| caste_category                 | varchar(64)                    | YES  |     | NULL    |       |
| pr_of_cg                       | enum('true','false','unknown') | YES  |     | NULL    |       |
| has_residence_certificate      | enum('true','false','unknown') | YES  |     | NULL    |       |
| ration_card_type               | varchar(64)                    | YES  |     | NULL    |       |
| ptgo_or_pvtg                   | enum('true','false','unknown') | YES  |     | NULL    |       |
| are_forest_dwellers            | enum('true','false','unknown') | YES  |     | NULL    |       |
| has_phone                      | enum('true','false','unknown') | YES  |     | NULL    |       |
| has_neighbourhood_phone_number | enum('true','false','unknown') | YES  |     | NULL    |       |
+--------------------------------+--------------------------------+------+-----+---------+-------+

+--------------------------+----------------------------------------------------------------+------+-----+---------+-------+
| Field                    | Type                                                           | Null | Key | Default | Extra |
+--------------------------+----------------------------------------------------------------+------+-----+---------+-------+
| id                       | varchar(8)                                                     | NO   | PRI | NULL    |       |
| family_id                | varchar(32)                                                    | YES  | MUL | NULL    |       |
| dob                      | date                                                           | YES  |     | NULL    |       |
| gender                   | enum('male','female','other','unknown')                        | YES  |     | NULL    |       |
| family_role              | enum('grandparent','father','mother','child','in-law','other') | YES  |     | NULL    |       |
| disadvantaged            | enum('true','false','unknown')                                 | YES  |     | NULL    |       |
| job                      | varchar(256)                                                   | YES  |     | NULL    |       |
| job_type                 | varchar(128)                                                   | YES  |     | NULL    |       |
| in_educational_institute | enum('true','false','unknown')                                 | YES  |     | NULL    |       |
| education_level          | varchar(64)                                                    | YES  |     | NULL    |       |
| prev_year_tenth          | enum('true','false','unknown')                                 | YES  |     | NULL    |       |
| prev_year_twelfth        | enum('true','false','unknown')                                 | YES  |     | NULL    |       |
| tenth_percentage_marks   | float(5,2)                                                     | YES  |     | NULL    |       |
| twelfth_percentage_marks | float(5,2)                                                     | YES  |     | NULL    |       |
| tenth_top_ten            | enum('true','false','unknown')                                 | YES  |     | NULL    |       |
| twelfth_top_ten          | enum('true','false','unknown')                                 | YES  |     | NULL    |       |
| has_bocw_card            | enum('true','false','unknown')                                 | YES  |     | NULL    |       |
| bocw_card_issue_date     | date                                                           | YES  |     | NULL    |       |
| has_uow_card             | enum('true','false','unknown')                                 | YES  |     | NULL    |       |
| uow_card_issue_date      | date                                                           | YES  |     | NULL    |       |
| pregnancy                | enum('true','false','unknown')                                 | YES  |     | NULL    |       |
| name                     | varchar(128)                                                   | YES  |     | NULL    |       |
+--------------------------+----------------------------------------------------------------+------+-----+---------+-------+
        """

def main():
    InitGlobals()
    LoadBeneficiariesFromFile('maago/data/survey_data_may.csv')
    beneficiarySchemes = GetBeneficiarySchemesMapping()    
    
    # get the schema
    if len(beneficiarySchemes) > 0:
        sampleBeneficiaryKey = list(beneficiarySchemes.keys())[0]
        schema = list(beneficiarySchemes[sampleBeneficiaryKey].keys())
        values = list(beneficiarySchemes.values())
        try:
            with open("result.csv", 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=schema)
                writer.writeheader()
                for data in values:
                    writer.writerow(data)
        except IOError:
            print("I/O error")
        
    return 0


if __name__ == '__main__':
    sys.exit(main())
