#!/usr/bin/env python
#
# Angshuman Guha
# angshuman.guha@gmail.com

import sys
from loaders.beneficiary_scheme_mapping import GetBeneficiarySchemesMapping


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
        """


def main():
    # LoadBeneficiaries('maago/data/survey_data_may.csv')
    beneficiarySchemes = GetBeneficiarySchemesMapping()

    print(beneficiarySchemes)

    return 0


if __name__ == '__main__':
    sys.exit(main())
