from app.db import insert_location, insert_family, insert_family_member
from utils.beneficiary_utils import new_family
from utils.csv import CSVLoader, getMappingFromCSVLoaderResponse
from utils.db import GetDBConnection
from utils.dictionary import getMappedDict, splitCombinedDict
from utils.normalization import (
    get_normalised_date_value,
    get_normalised_float_value,
    get_normalised_string_value,
    get_normalised_bool_value,
)
from utils.random import GetAlphaNumericString
from utils import proximity_score

from thefuzz import fuzz

UNKNOWN_STRING = "unknown"


def LoadBeneficiariesFromFile(dataFileName, loadToDB=True):
    beneficiaries = []
    for beneficiary in CSVLoader(dataFileName):
        beneficiaries.append(beneficiary)
    print("%d beneficiaries" % len(beneficiaries))
    if loadToDB:
        PushBeneficiariesToDB(beneficiaries)
    return beneficiaries


def LoadBeneficiariesFromDB():
    pass


def PushBeneficiariesToDB(beneficiaries):
    # get various mappings
    global familyMapping
    global locationMapping
    global respondentMapping
    global familyMembersMapping
    global pregnancyMapping
    familyMapping = getMappingFromCSVLoaderResponse(
        CSVLoader("config/familyMapping.csv")
    )
    locationMapping = getMappingFromCSVLoaderResponse(
        CSVLoader("config/locationMapping.csv")
    )
    respondentMapping = getMappingFromCSVLoaderResponse(
        CSVLoader("config/respondentMapping.csv")
    )
    familyMembersMapping = getMappingFromCSVLoaderResponse(
        CSVLoader("config/familyMembersMapping.csv")
    )
    pregnancyMapping = getMappingFromCSVLoaderResponse(
        CSVLoader("config/pregnancyMapping.csv")
    )
    families = []
    # For each beneficiary, create a structured (family) object out of it divided as family, respondent and family member data
    for beneficiary in beneficiaries:
        # For each beneficiary row construct a family object
        family = newFamily(beneficiary)
        families.append(family)
    dbConnection = GetDBConnection()

    # Push data in mysql db
    pushToDB(dbConnection, families)

    # commit db transactions
    dbConnection.commit()

    dbConnection.close()


def load_beneficiaries_to_db(beneficiaries):
    families = []
    # For each beneficiary, create a structured (family) object out of it divided as family, respondent and family member data
    for beneficiary in beneficiaries:
        # For each beneficiary row construct a family object
        family = new_family(beneficiary)
        load_family_to_db(family)
        families.append(family)
    return families
    # pass


def newFamily(beneficiary):
    # create a new family
    family = getMappedDict(familyMapping, beneficiary)

    # assign location to the family
    location = getMappedDict(locationMapping, beneficiary)
    family["location"] = location

    # get respondent
    respondent = getMappedDict(respondentMapping, beneficiary)

    # TODO: Handle other job
    # add other family members
    familyMembersCombinedDict = getMappedDict(familyMembersMapping, beneficiary)

    # split the dict into various family members array
    family["members"] = splitCombinedDict(familyMembersCombinedDict)

    # Figure out family roles of the members based on relationship with the respondent
    parentFound = False

    # it may happen that the respondent is a parent, in which case we need to keep track
    # of the husband or wife and use it later to assign proper role
    wifeIndex = -1
    husbandIndex = -1
    for i, member in enumerate(family["members"]):
        familyRole = UNKNOWN_STRING
        relationshipWithRespondent = member["relationshipWithRespondent"]

        if relationshipWithRespondent == "father":
            familyRole = "father"
            parentFound = True
        elif relationshipWithRespondent == "mother":
            familyRole = "mother"
            parentFound = True
        elif relationshipWithRespondent in ["child", "brother", "sister", "sibling"]:
            familyRole = "child"
        elif "inlaw" in relationshipWithRespondent.replace("-", "").lower():
            familyRole = "in-law"
        elif relationshipWithRespondent == "husband":
            husbandIndex = i
        elif relationshipWithRespondent == "wife":
            wifeIndex = i
        elif relationshipWithRespondent in ["", "other"]:
            familyRole = "other"
        member["familyRole"] = familyRole

    # figure out family role the respondent using the family roles of other members
    respondentFamilyRole = UNKNOWN_STRING
    if not parentFound:
        if respondent["gender"] == "male":
            respondentFamilyRole = "father"
            if wifeIndex >= 0:
                family["members"][wifeIndex]["familyRole"] = "mother"
        elif respondent["gender"] == "female":
            respondentFamilyRole = "mother"
            if husbandIndex >= 0:
                family["members"][husbandIndex]["familyRole"] = "father"
    else:
        respondentFamilyRole = "child"

    # populate pregnancy status
    # get the names of the pregnant women of the family from the pregnancy mapping
    # use fuzzy string matching to figure out which of the family's members are pregnant
    # update the pregnancy status of these family members
    pregnantWomensCombinedDict = getMappedDict(pregnancyMapping, beneficiary)
    # current data has a provision of only two pregnant women, so pass two
    pregnantWomen = splitCombinedDict(pregnantWomensCombinedDict, 2)
    for p in pregnantWomen:
        fuzzyScore = -999
        pIndex = -1
        pName = p["name"].strip()
        if pName == "":
            continue

        for i, m in enumerate(family["members"] + [respondent]):
            memberName = m["name"]
            if memberName == "":
                continue
            # using simple ratio for now, will tweak later if needed
            f = fuzz.ratio(pName, memberName)
            if f > fuzzyScore:
                fuzzyScore = f
                pIndex = i
        if pIndex >= 0 and pIndex < (len(family["members"]) - 1):
            family["members"][pIndex]["pregnancy"] = "yes"
        elif pIndex == (len(family["members"]) - 1):
            respondent["pregnancy"] = "yes"

    for m in family["members"] + [respondent]:
        if m["gender"] == "male":
            m["pregnancy"] = "no"
        elif "pregnancy" not in m or m["pregnancy"] == "":
            m["pregnancy"] = UNKNOWN_STRING

    respondent["familyRole"] = respondentFamilyRole

    # no data regarding some of the respondent's field. use unknown
    respondent["disadvantaged"] = UNKNOWN_STRING
    respondent["prevYearTenth"] = UNKNOWN_STRING
    respondent["prevYearTwelfth"] = UNKNOWN_STRING
    respondent["tenthTopTen"] = UNKNOWN_STRING
    respondent["twelfthTopTen"] = UNKNOWN_STRING
    respondent["jobType"] = UNKNOWN_STRING
    respondent["tenthPercentageMarks"] = get_normalised_float_value("-19")
    respondent["twelfthPercentageMarks"] = get_normalised_float_value("-19")
    # add respondent to the family member
    family["members"].append(respondent)

    return family


# # TODO: Add type conversion
# def lookupBeneficiary(beneficiary, key):
#     value = ""

#     if key in mappedHeaders.keys():
#         value = beneficiary[mappedHeaders[key]['dataHeader']]

#     return value


def load_family_to_db(family):
    location = family["location"]
    if location["pincode"] == "":
        location["pincode"] = "0"
    if location["wardNumber"] == "":
        location["wardNumber"] = "0"
    locationID = insert_location(location)
    familyID = insert_family(family, locationID)
    for member in family["members"]:
        insert_family_member(member, familyID)


def pushToDB(dbConnection, families):
    cursor = dbConnection.cursor()
    print("starting to push %d families to db..." % len(families))
    for f in families:
        # TODO: Check if the location exists before inserting the location
        # Create location for the row, get the location ID
        fLocation = f["location"]
        locationID = GetAlphaNumericString(8)

        # HACK: Zero out empty strings for numeric columns
        if fLocation["pincode"] == "":
            fLocation["pincode"] = "-1111"
        if fLocation["wardNumber"] == "":
            fLocation["wardNumber"] = "-1111"

        createLocationQuery = (
            """INSERT INTO locations (id, location_type, locality, pincode, ward_number, ward_name, village, survey_village_town_city) VALUES ('%s', '%s', '%s', %s, %s, '%s', '%s', '%s');"""
            % (
                locationID,
                fLocation["areaType"],
                fLocation["areaLocality"],
                fLocation["pincode"],
                fLocation["wardNumber"],
                fLocation["wardName"],
                fLocation["village"],
                fLocation["surveyVillageTownCity"],
            )
        )

        cursor.execute(createLocationQuery)

        # Create family for the row, get the family ID
        familyID = f["id"]

        # calculate boolean columns prOfCG, hasPhone, hasResidenceCertificate, hasNeighbourhoodPhone, ptgoOrPVTG, areForestDwellers
        prOfCG = get_normalised_bool_value(f["prOfCG"])
        hasPhone = get_normalised_bool_value(f["hasPhone"])
        hasResidenceCertificate = get_normalised_bool_value(
            f["hasResidenceCertificate"]
        )
        hasNeighbourhoodPhoneNumber = get_normalised_bool_value(
            str(f["neighbourhoodPhone"] != "")
        )
        ptgoOrPVTG = get_normalised_bool_value(f["ptgoOrPVTG"])
        areForestDwellers = get_normalised_bool_value(f["areForestDwellers"])

        createFamilyQuery = (
            """INSERT INTO families (id, location_id, caste, caste_category, pr_of_cg, has_residence_certificate, ration_card_type, ptgo_or_pvtg, are_forest_dwellers, has_phone, has_neighbourhood_phone_number) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"""
            % (
                familyID,
                locationID,
                f["caste"],
                f["casteCategory"],
                prOfCG,
                hasResidenceCertificate,
                f["rationCardType"],
                ptgoOrPVTG,
                areForestDwellers,
                hasPhone,
                hasNeighbourhoodPhoneNumber,
            )
        )
        cursor.execute(createFamilyQuery)

        # Create family members
        familyMembers = f["members"]
        for m in familyMembers:
            # Treat name as the primary key in data
            if m["name"] in ["", UNKNOWN_STRING]:
                continue
            memberID = GetAlphaNumericString(8)

            # calculate boolean columns
            # disadvantaged, inEducationalInstitute, prevYearTenth, prevYearTwelfth
            # tenthTopTen, twelfthTopTen
            # hasBOCWCard, hasUOWCard
            disadvantaged = get_normalised_bool_value(m["disadvantaged"])
            inEducationalInstitute = get_normalised_bool_value(
                m["inEducationalInstitute"]
            )
            prevYearTenth = get_normalised_bool_value(m["prevYearTenth"])
            prevYearTwelfth = get_normalised_bool_value(m["prevYearTwelfth"])
            tenthTopTen = get_normalised_bool_value(m["tenthTopTen"])
            twelfthTopTen = get_normalised_bool_value(m["twelfthTopTen"])
            hasBOCWCard = get_normalised_bool_value(m["hasBOCWCard"])
            hasUOWCard = get_normalised_bool_value(m["hasUOWCard"])
            pregnancy = get_normalised_bool_value(m["pregnancy"])

            # calculate date columns
            # dob, bocwCardIssueDate, uowCardIssueDate
            dob = get_normalised_date_value(m["dob"])
            bocwCardIssueDate = get_normalised_date_value(m["bocwCardIssueDate"])
            uowCardIssueDate = get_normalised_date_value(m["uowCardIssueDate"])

            # calculate numerical columns
            # tenthPercentageMarks, twelfthPercentageMarks
            tenthPercentageMarks = get_normalised_float_value(m["tenthPercentageMarks"])
            twelfthPercentageMarks = get_normalised_float_value(
                m["twelfthPercentageMarks"]
            )

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
                job_type,
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
            )""" % (
                memberID,
                familyID,
                m["name"],
                dob,
                get_normalised_string_value(m["gender"]),
                m["familyRole"],
                disadvantaged,
                pregnancy,
                m["job"],
                m["jobType"],
                inEducationalInstitute,
                m["educationLevel"],
                prevYearTenth,
                prevYearTwelfth,
                tenthPercentageMarks,
                twelfthPercentageMarks,
                tenthTopTen,
                twelfthTopTen,
                hasBOCWCard,
                bocwCardIssueDate,
                hasUOWCard,
                uowCardIssueDate,
            )

            cursor.execute(createFamilyMemberQuery)

    # close the cursor
    cursor.close()
