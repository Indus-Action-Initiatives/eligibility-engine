#!/usr/bin/env python
#
# Angshuman Guha
# angshuman.guha@gmail.com

import csv
import random
import sys
import mysql.connector
from mysql.connector import Error
from common.util import GetAlphaNumericString
class SimpleCSVLoader:
    # single header row
    def __init__(self, filename):
        try:
            f = open(filename, encoding='utf-8-sig')
            self.reader = csv.DictReader(f)
        except:
            print('cannot load beneficiary file: %s' % filename, file=sys.stderr)
            raise
    def __iter__(self):
        for x in self.reader:
            yield x

class CSVLoader:
    def __init__(self, filename, numHeader=1, useLastHeader=True):
        assert numHeader >= 1
        headers = []
        try:
            f = open(filename, encoding='utf-8-sig')
            reader = csv.reader(f)
        except:
            print('cannot load CSV file: %s' % filename, file=sys.stderr)
            raise
        for i in range(numHeader):
            headers.append(reader.__next__())
        self.header = []
        for i in range(len(headers[0])):
            tmp = []
            for header in headers:
                h = header[i].strip()
                if h:
                    tmp.append(h)
            if useLastHeader:
                self.header.append(tmp[-1])
            else:
                self.header.append(' '.join(tmp))
        f.close()
        f = open(filename, encoding='utf-8-sig')
        self.reader = csv.DictReader(f, fieldnames = self.header)
        for x in self.reader:
            numHeader -= 1
            if numHeader == 0:
                break
    def __iter__(self):
        for x in self.reader:
            yield x

State = 'State'
Sector = 'Sector'
Scheme = 'Scheme'
SubScheme = 'Sub-Scheme'
IDiSchemeSubDiv = 'IDi scheme sub-divisions'

def LoadSchemes():
    schemes = []
    n = 0
    for scheme in CSVLoader('maago/config/benefitsCG.csv', numHeader=2):
        n += 1
        if (scheme[State] == 'Chhattisgarh'
          and scheme[Sector] == 'Right to Livelihood'
          and scheme[Scheme] == 'BoCW'
          and (scheme[SubScheme] == 'Noni Sashaktikaran Scheme'
               or scheme[SubScheme] == 'Mini Mata Mahtari Jatan Yojna'
               or scheme[SubScheme] == 'Chief Minister Shramik Tool Assistance Scheme'
               or scheme[SubScheme] == 'Naunihal Scholarship Scheme'
               or (scheme[SubScheme] == 'Meritorious Student / Student Education Promotion Scheme'
                    and scheme[IDiSchemeSubDiv] == 'B')
               or (scheme[SubScheme] == 'Construction Workers Permanent Disability and Accidental Death Pension Scheme'
                    and scheme[IDiSchemeSubDiv] == 'B'))):
              schemes.append(scheme)
        elif (scheme[State] == 'Chhattisgarh'
          and scheme[Sector] == 'Right to Livelihood'
          and scheme[Scheme] == 'UoW'
          and scheme[SubScheme] == 'Chief Minister Unorganized Workers Cycle Assistance Scheme'):
              schemes.append(scheme)
    print('considering %d schemas out of %d' % (len(schemes), n))
    return schemes

def SchemeName(scheme):
    return ' : '.join([scheme[State], scheme[Sector], scheme[SubScheme], scheme[IDiSchemeSubDiv]])

def normalizeString(s):
    return ' '.join(s.split())

def match(beneficiary, scheme):
    print('chosen scheme: %s' % SchemeName(scheme))
    print('criteria:')
    for k, v in scheme.items():
        if v.strip():
            print('    %s = %s' % (normalizeString(k), normalizeString(v)))
    print('beneficiary attributes (total %d):' % len(beneficiary))
    for k,v in beneficiary.items():
        print('        %s' % (normalizeString(k)))
    for k, v in beneficiary.items():
        if v.strip():
            print('    %s = %s' % (normalizeString(k), normalizeString(v)))

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
            disabled: bool;
            job: string;
            jobType: string;
            jobID: int;            
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

familyMapping = {}
locationMapping = {}
respondentMapping = {}
familyMembersMapping = {}
# BAD CODE: FIX LATER
# Following functions assume that the mappings above are already populated populated

def getMappedDict(headerMapping, srcDict):
    destDict = {}

    for key in headerMapping.keys():       
        if key in srcDict.keys():
            # TODO: Use typecasting
            destDict[headerMapping[key]["dest"]] = srcDict[key]
    
    return destDict


# # TODO: Add type conversion
# def lookupBeneficiary(beneficiary, key):
#     value = ""

#     if key in mappedHeaders.keys():
#         value = beneficiary[mappedHeaders[key]['dataHeader']]
    
#     return value

# fm##1$$job
FAMILY_MEMBER_INDIVIDUAL_SEPARATOR = "##"
FAMILY_MEMBER_ATTRIBUTE_SEPARATOR = "$$"
# We probably don't need this. TODO: Remove if necessary.
# We are doing this so that no data is missed if any of he property is missing
MAXIMUM_NUMBER_OF_FAMILY_MEMBERS = 6

def splitFamilyMembersCombinedDict(familyMembersCombinedDict):
    otherFamilyMembers = []

    for i in range(MAXIMUM_NUMBER_OF_FAMILY_MEMBERS):
        otherFamilyMembers.append({})

    for key, value in familyMembersCombinedDict.items():
        idPlusAttribute = key.split(FAMILY_MEMBER_INDIVIDUAL_SEPARATOR)[1]
        idPlusAttribute = idPlusAttribute.split(FAMILY_MEMBER_ATTRIBUTE_SEPARATOR)
        id = int(idPlusAttribute[0]) - 1
        attribute = idPlusAttribute[1]        
        otherFamilyMembers[id][attribute] = value

    return otherFamilyMembers

def newFamily(beneficiary):
    # create a new family
    family = getMappedDict(familyMapping, beneficiary)

    # assign location to the family
    location = getMappedDict(locationMapping, beneficiary)
    family['location'] = location

    # get respondent
    respondent = getMappedDict(respondentMapping, beneficiary)

    # TODO: Handle other job
    # add other family members
    familyMembersCombinedDict = getMappedDict(familyMembersMapping, beneficiary)

    # split the dict into various family members array
    family['members'] = splitFamilyMembersCombinedDict(familyMembersCombinedDict)

    # Figure out family roles of the members based on relationship with the respondent
    parentFound = False
    for member in family['members']:
        familyRole = 'unknown'
        relationshipWithRespondent = member['relationshipWithRespondent']        

        if relationshipWithRespondent == 'father':
            familyRole = 'father'
            parentFound = True
        elif relationshipWithRespondent == 'mother':
            familyRole = 'mother'
            parentFound = True
        elif relationshipWithRespondent in ['brother', 'sister', 'sibling']:
            familyRole = 'child'
        elif "in-law" in relationshipWithRespondent:
            familyRole = 'in-law'
        
        member['familyRole'] = familyRole

    # figure out family role the respondent using the family roles of other members
    respondentFamilyRole = 'unknown'
    if not parentFound:
       if respondent['gender'] == 'male':
           respondentFamilyRole = 'father'
       elif respondent['gender'] == 'female':
           respondentFamilyRole = 'mother'
    else:
        respondentFamilyRole = 'child'

    respondent['familyRole'] = respondentFamilyRole

    # add respondent to the family member
    family['members'].append(respondent)   

    return family

def getMappingFromCSVLoaderResponse(resp):
    retVal = {}

    for row in resp:
        retVal[row['src']] = {'dest': row['dest'], 'dataType': row['dataType']}

    return retVal

def pushToDB(dbConnection, families):
    cursor = dbConnection.cursor()
    print("starting to push %d families to db..." % len(families))
    for f in families:
        # TODO: Check if the location exists before inserting the location
        # Create location for the row, get the location ID
        fLocation = f['location']
        locationID = GetAlphaNumericString(8)

        # HACK: Zero out empty strings for numeric columns
        if fLocation['pincode'] == '':
            fLocation['pincode'] = '0'
        if fLocation['wardNumber'] == '':
            fLocation['wardNumber'] = '0'

        createLocationQuery = """INSERT INTO locations (id, location_type, locality, pincode, ward_number, ward_name, village, survey_village_town_city) VALUES ('%s', '%s', '%s', %s, %s, '%s', '%s', '%s');""" % (locationID, fLocation['areaType'], fLocation['areaLocality'], fLocation['pincode'], fLocation['wardNumber'], 
               fLocation['wardName'], fLocation['village'], fLocation['surveyVillageTownCity'])
        
        cursor.execute(createLocationQuery)
        print(cursor.lastrowid)

        # Create family for the row, get the family ID


        # Create family members

    # close the cursor
    cursor.close()
    

def main():
    schemes = LoadSchemes()
    beneficiaries = []
    families = []
    
    for beneficiary in CSVLoader('maago/data/survey_data_may.csv'):
        beneficiaries.append(beneficiary)
        break
    print('%d beneficiaries' % len(beneficiaries))

    # get various mappings
    global familyMapping
    global locationMapping
    global respondentMapping
    global familyMembersMapping
    familyMapping = getMappingFromCSVLoaderResponse(CSVLoader('maago/config/familyMapping.csv'))
    locationMapping = getMappingFromCSVLoaderResponse(CSVLoader('maago/config/locationMapping.csv'))
    respondentMapping = getMappingFromCSVLoaderResponse(CSVLoader('maago/config/respondentMapping.csv'))
    familyMembersMapping = getMappingFromCSVLoaderResponse(CSVLoader('maago/config/familyMembersMapping.csv'))
   
    # For each beneficiary, create a structured (family) object out of it divided as family, respondent and family member data
    for beneficiary in beneficiaries:
        # For each beneficiary row construct a family object
        family = newFamily(beneficiary);
        families.append(family)

    # TODO: get connection on demand
    dbConnection = mysql.connector.connect(
        host='localhost',
        user='maago',
        passwd='maagoindus',
        db='ee'
    )
    try:
        if dbConnection.is_connected():
            print("connected to the mysql db")           
    except Error as e:
        print("error: ", e)

    # Push data in mysql db
    pushToDB(dbConnection, families)

    scheme = random.choice(schemes)
    beneficiary = random.choice(beneficiaries)
    #match(beneficiary, scheme)

    # commit db transactions
    dbConnection.commit()

    dbConnection.close()

    return 0

if __name__ == '__main__':
    sys.exit(main())
