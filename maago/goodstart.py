#!/usr/bin/env python
#
# Angshuman Guha
# angshuman.guha@gmail.com

import csv
import sys
import mysql.connector
from mysql.connector import Error
from common.util import GetAlphaNumericString, GetNormalisedValue, GetDBDateString, GetDBFloatString, GetNormalisedStringValue
from thefuzz import fuzz
import re

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

# def LoadSchemes():
#     schemes = []
#     n = 0
#     for scheme in CSVLoader('maago/config/benefitsCG.csv', numHeader=2):
#         n += 1
#         if (scheme[State] == 'Chhattisgarh'
#           and scheme[Sector] == 'Right to Livelihood'
#           and scheme[Scheme] == 'BoCW'
#           and (scheme[SubScheme] == 'Noni Sashaktikaran Scheme'
#                or scheme[SubScheme] == 'Mini Mata Mahtari Jatan Yojna'
#                or scheme[SubScheme] == 'Chief Minister Shramik Tool Assistance Scheme'
#                or scheme[SubScheme] == 'Naunihal Scholarship Scheme'
#                or (scheme[SubScheme] == 'Meritorious Student / Student Education Promotion Scheme'
#                     and scheme[IDiSchemeSubDiv] == 'B')
#                or (scheme[SubScheme] == 'Construction Workers Permanent Disability and Accidental Death Pension Scheme'
#                     and scheme[IDiSchemeSubDiv] == 'B'))):
#               schemes.append(scheme)
#         elif (scheme[State] == 'Chhattisgarh'
#           and scheme[Sector] == 'Right to Livelihood'
#           and scheme[Scheme] == 'UoW'
#           and scheme[SubScheme] == 'Chief Minister Unorganized Workers Cycle Assistance Scheme'):
#               schemes.append(scheme)
#     print('considering %d schemas out of %d' % (len(schemes), n))
#     return schemes

def LoadSchemes():
    schemes = CSVLoader('maago/config/schemes.csv')

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

familyMapping = {}
locationMapping = {}
respondentMapping = {}
familyMembersMapping = {}
pregnancyMapping = {}
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
INDIVIDUAL_SEPARATOR = "##"
ATTRIBUTE_SEPARATOR = "$$"
# We probably don't need this. TODO: Remove if necessary.
# We are doing this so that no data is missed if any of he property is missing
MAXIMUM_NUMBER_OF_FAMILY_MEMBERS = 6

def splitCombinedDict(combinedDict, numberOfMembers=MAXIMUM_NUMBER_OF_FAMILY_MEMBERS):
    otherFamilyMembers = []

    for i in range(numberOfMembers):
        otherFamilyMembers.append({})

    for key, value in combinedDict.items():
        idPlusAttribute = key.split(INDIVIDUAL_SEPARATOR)[1]
        idPlusAttribute = idPlusAttribute.split(ATTRIBUTE_SEPARATOR)
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
    family['members'] = splitCombinedDict(familyMembersCombinedDict)

    # Figure out family roles of the members based on relationship with the respondent
    parentFound = False

    # it may happen that the respondent is a parent, in which case we need to keep track
    # of the husband or wife and use it later to assign proper role
    wifeIndex = -1
    husbandIndex = -1
    for i, member in enumerate(family['members']):
        familyRole = 'unknown'
        relationshipWithRespondent = member['relationshipWithRespondent']        

        if relationshipWithRespondent == 'father':
            familyRole = 'father'
            parentFound = True
        elif relationshipWithRespondent == 'mother':
            familyRole = 'mother'
            parentFound = True
        elif relationshipWithRespondent in ['child', 'brother', 'sister', 'sibling']:
            familyRole = 'child'
        elif "inlaw" in relationshipWithRespondent.replace("-", "").lower():
            familyRole = 'in-law'
        elif relationshipWithRespondent == 'husband':
            husbandIndex = i
        elif relationshipWithRespondent == 'wife':
            wifeIndex = i
        elif relationshipWithRespondent in ['', 'other']:
            familyRole = 'other'
        member['familyRole'] = familyRole

     # figure out family role the respondent using the family roles of other members
    respondentFamilyRole = 'unknown'
    if not parentFound:
       if respondent['gender'] == 'male':
           respondentFamilyRole = 'father'
           if wifeIndex >= 0:
               family['members'][wifeIndex]['familyRole'] = 'mother'
       elif respondent['gender'] == 'female':
           respondentFamilyRole = 'mother'
           if husbandIndex >= 0:
               family['members'][husbandIndex]['familyRole'] = 'father'
    else:
        respondentFamilyRole = 'child' 

    # populate pregnancy status
    # get the names of the pregnant women of the family from the pregnancy mapping
    # use fuzzy string matching to figure out which of the family's members are pregnant
    # update the pregnancy status of these family members
    pregnantWomensCombinedDict = getMappedDict(pregnancyMapping, beneficiary)
    # current data has a provision of only two pregnant women, so pass two
    pregnantWomen = splitCombinedDict(pregnantWomensCombinedDict, 2)
    familyMembersNames = []
    for p in pregnantWomen:
        fuzzyScore = -999
        pIndex = -1
        pName = p['name'].strip()
        if pName == '':
            continue
      
        for i, m in enumerate(family['members'] + [respondent]):
            memberName = m['name']
            if memberName == '':
                continue
            # using simple ratio for now, will tweak later if needed
            f = fuzz.ratio(pName, memberName) 
            if f > fuzzyScore:
                fuzzyScore = f
                pIndex = i
        if pIndex >= 0 and pIndex < (len(family['members']) - 1):            
            family['members'][pIndex]['pregnancy'] = 'yes'
        elif pIndex == (len(family['members']) - 1):
            respondent['pregnancy'] = 'yes'

    for m in (family['members'] + [respondent]):
        if m['gender'] == 'male':
            m['pregnancy'] = 'no'
        elif 'pregnancy' not in m or m['pregnancy'] == '':
            m['pregnancy'] = 'unknown'   

    respondent['familyRole'] = respondentFamilyRole

    # no data regarding some of the respondent's field. use unknown
    respondent['disadvantaged'] = 'unknown'
    respondent['prevYearTenth'] = 'unknown'
    respondent['prevYearTwelfth'] = 'unknown'
    respondent['tenthTopTen'] = 'unknown'
    respondent['twelfthTopTen'] = 'unknown'
    respondent['jobType'] = 'unknown'
    respondent['tenthPercentageMarks'] = GetDBFloatString('-1')
    respondent['twelfthPercentageMarks'] = GetDBFloatString('-1')

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

        # Create family for the row, get the family ID
        familyID = f['id']

        # calculate boolean columns prOfCG, hasPhone, hasResidenceCertificate, hasNeighbourhoodPhone, ptgoOrPVTG, areForestDwellers
        prOfCG = GetNormalisedValue(f['prOfCG'])
        hasPhone = GetNormalisedValue(f['hasPhone'])
        hasResidenceCertificate = GetNormalisedValue(f['hasResidenceCertificate'])
        hasNeighbourhoodPhoneNumber = GetNormalisedValue(str(f['neighbourhoodPhone'] != ''))
        ptgoOrPVTG = GetNormalisedValue(f['ptgoOrPVTG'])
        areForestDwellers = GetNormalisedValue(f['areForestDwellers'])

        createFamilyQuery = """INSERT INTO families (id, location_id, caste, caste_category, pr_of_cg, has_residence_certificate, ration_card_type, ptgo_or_pvtg, are_forest_dwellers, has_phone, has_neighbourhood_phone_number) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')""" % (
            familyID, locationID, f['caste'],  f['casteCategory'], prOfCG, hasResidenceCertificate, f['rationCardType'], ptgoOrPVTG, areForestDwellers, hasPhone, hasNeighbourhoodPhoneNumber
        )
        cursor.execute(createFamilyQuery)

        # Create family members
        familyMembers = f['members']
        for m in familyMembers:
            # Treat name as the primary key in data
            if m['name'] == '':
                continue
            memberID = GetAlphaNumericString(8)

            # calculate boolean columns
            # disadvantaged, inEducationalInstitute, prevYearTenth, prevYearTwelfth
            # tenthTopTen, twelfthTopTen
            # hasBOCWCard, hasUOWCard
            disadvantaged = GetNormalisedValue(m['disadvantaged'])
            inEducationalInstitute = GetNormalisedValue(m['inEducationalInstitute'])
            prevYearTenth = GetNormalisedValue(m['prevYearTenth'])
            prevYearTwelfth = GetNormalisedValue(m['prevYearTwelfth'])
            tenthTopTen = GetNormalisedValue(m['tenthTopTen'])
            twelfthTopTen = GetNormalisedValue(m['twelfthTopTen'])
            hasBOCWCard = GetNormalisedValue(m['hasBOCWCard'])
            hasUOWCard = GetNormalisedValue(m['hasUOWCard'])
            pregnancy = GetNormalisedValue(m['pregnancy'])

            # calculate date columns
            # dob, bocwCardIssueDate, uowCardIssueDate
            dob = GetDBDateString(m['dob'])
            bocwCardIssueDate = GetDBDateString(m['bocwCardIssueDate'])
            uowCardIssueDate = GetDBDateString(m['uowCardIssueDate'])

            # calculate numerical columns
            # tenthPercentageMarks, twelfthPercentageMarks
            tenthPercentageMarks = GetDBFloatString(m['tenthPercentageMarks'])
            twelfthPercentageMarks = GetDBFloatString(m['twelfthPercentageMarks'])            

            createFamilyMemberQuery = """INSERT INTO family_members (
                id,
                family_id,
                name,
                dob,
                gender,
                family_role,
                disadvantaged,
                pregnancy,
                job,
                jobType,
                in_educational_institute,
                education_level,
                prev_year_tenth,
                prev_year_twelfth,
                tenth_percentage_marks,
                twelfth_percentage_marks,
                tenth_top_ten,
                twelfth_top_ten,
                has_bocw_card,
                bocw_card_issue_date,
                has_uow_card,
                uow_card_issue_date                
            ) VALUES (
                '%s',
                '%s',
                '%s',
                %s,
                '%s',
                '%s',
                '%s',
                '%s',
                '%s',
                '%s',
                '%s',
                '%s',
                '%s',
                '%s',
                %s,
                %s,
                '%s',
                '%s',
                '%s',
                %s,
                '%s',
                %s
            )""" % (memberID, familyID, m['name'], dob, GetNormalisedStringValue(m['gender']), m['familyRole'], disadvantaged, pregnancy, m['job'],
                    m['jobType'], inEducationalInstitute, m['educationLevel'], prevYearTenth,
                    prevYearTwelfth, tenthPercentageMarks, twelfthPercentageMarks, tenthTopTen,
                    twelfthTopTen, hasBOCWCard, bocwCardIssueDate, hasUOWCard, uowCardIssueDate)
            
            cursor.execute(createFamilyMemberQuery)

    # close the cursor
    cursor.close()

# Assumptions:
# 1. Each criterion is enclosed in a pair of parenthesis
# 2. In case of nested parenthesis, the inner parenthesis will be ignored
# 3. Criteria are connected with only AND, ORs are not allowed as connectors
# 4. ORs are always inside the token, i.e. within the parenthesis
def getCriteriaTokensFromInclusionCriteria(criteria):
    tokens = []

    openingParentheses = closingParentheses = 0    
    currentToken = ''
    for char in criteria:
        if char == '(':
            openingParentheses += 1
        if char == ')':
            closingParentheses += 1

        if openingParentheses > 0:
            currentToken += char

        # ignore the expression connectors, assuming it's always an AND
        if openingParentheses == closingParentheses and openingParentheses > 0:            
            tokens.append(currentToken)
            currentToken = ''
            openingParentheses = closingParentheses = 0
    
    return tokens

def getColumnsFromCriterion(criterion):
    return re.findall('fm\.\w+|f\.\w+', criterion)
    
# UNKNOWN_SCORE = 0.001
# UNKNOWN_STRING = 'maago__unknown'
# UNKNOWN_NUMBER = '-111111'
# UNKNOWN_DATE = '01-01-1800'
# def getCriterionStringFromCriteriaToken(ct):
    

def main():
    schemes = LoadSchemes()
    beneficiaries = []
    families = []
    
    for beneficiary in CSVLoader('maago/data/survey_data_may.csv'):
        beneficiaries.append(beneficiary)
       
    print('%d beneficiaries' % len(beneficiaries))

    # get various mappings
    global familyMapping
    global locationMapping
    global respondentMapping
    global familyMembersMapping
    global pregnancyMapping
    familyMapping = getMappingFromCSVLoaderResponse(CSVLoader('maago/config/familyMapping.csv'))
    locationMapping = getMappingFromCSVLoaderResponse(CSVLoader('maago/config/locationMapping.csv'))
    respondentMapping = getMappingFromCSVLoaderResponse(CSVLoader('maago/config/respondentMapping.csv'))
    familyMembersMapping = getMappingFromCSVLoaderResponse(CSVLoader('maago/config/familyMembersMapping.csv'))
    pregnancyMapping = getMappingFromCSVLoaderResponse(CSVLoader('maago/config/pregnancyMapping.csv'))
   
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

    # commit db transactions
    dbConnection.commit()

    cursor = dbConnection.cursor()
    scheme_beneficiaries = {}
    # get all the eligible members for each family using the inclusion criteria for the scheme
    for s in schemes:
        inclusionCriteria = s['inclusion_criteria']
        criteria = getCriteriaTokensFromInclusionCriteria(inclusionCriteria)
        # TODO: Add exclusion criteria

        # get column from the criteria
        criteriaColumns = {}
        for i, c in enumerate(criteria):
            criteriaColumns['criteria%d' % i] = getColumnsFromCriterion(c)
        columns = set()
        for values in criteriaColumns.values():
            for v in values:
                columns.add(v)

        # generate criteria string
        # criteria = [getCriterionStringFromCriteriaToken(c) for c in criteria]
        # criteriaString = ', '.join(criteria)
        # generate the select clause 

        criteriaStrings = []
        for i, c in enumerate(criteria):
            criteriaStrings.append('CASE WHEN %s THEN 1 ELSE 0 END AS criteria%d' % (c, i))
        mainCriteriaString = '(CASE WHEN %s THEN 1 ELSE 0 END) as main_criteria' % inclusionCriteria
        fromClause = ' FROM families as f INNER JOIN family_members as fm ON f.id = fm.family_id'
        eligibilityQuery = 'SELECT ' + ', '.join(columns) + ', ' + ', '.join(criteriaStrings)         + ', ' + mainCriteriaString + ', f.id as family_id, fm.id as member_id' + fromClause

        # eligibilityQuery = """SELECT f.id as family_id, fm.id as member_id, %s from families as f INNER JOIN 
        # family_members as fm ON f.id = fm.family_id WHERE %s""" % criteriaString

        print(eligibilityQuery)

        cursor.execute(eligibilityQuery)        
        result = cursor.fetchall()
        print(result)

    cursor.close()
    dbConnection.close()

    # scheme = random.choice(schemes)
    # beneficiary = random.choice(beneficiaries)
    # result = match(beneficiary, scheme)
    # print(result)
    return 0

if __name__ == '__main__':
    sys.exit(main())
