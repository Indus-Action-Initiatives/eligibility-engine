from loaders.config_loaders import get_config_mappings
from utils.dictionary import getMappedDict, splitCombinedDict
from utils.normalization import GetDBFloatString
from thefuzz import fuzz

config = get_config_mappings()
# TODO: Move to constants
UNKNOWN_STRING = 'unknown'


def new_family(beneficiary):
    # family = init_family(beneficiary)
    family = beneficiary
    parentFound = determine_family_roles(family)

    respondent = init_respondent(beneficiary, parentFound)
    populate_pregnancy_status(family, respondent, beneficiary)

    # add respondent to the family member
    family['members'].append(respondent)
    return family


def init_family(beneficiary):
    # create a new family and returns it
    family = getMappedDict(config['familyMapping'], beneficiary)

    # assign location to the family
    family['location'] = getMappedDict(config['locationMapping'], beneficiary)

    # TODO: Handle other job
    # add other family members
    # split the dict into various family members array
    familyMembersCombinedDict = getMappedDict(
        config['familyMembersMapping'], beneficiary)
    family['members'] = splitCombinedDict(familyMembersCombinedDict)

    return family


def determine_family_roles(family) -> bool:
    parentFound = False
    for i, member in enumerate(family['members']):
        # import pdb
        # pdb.set_trace()
        if 'relationshipWithRespondent' not in member:
            continue
        memberRole, parent = determine_family_member_role(member)
        parentFound = parent
        member['familyRole'] = memberRole
        if member['relationshipWithRespondent'] == 'husband' and parent:
            member['familyRole'] = 'father'
        elif member['relationshipWithRespondent'] == 'wife' and parent:
            member['familyRole'] = 'mother'

    return parentFound


def determine_family_member_role(member):

    relationshipWithRespondent = member['relationshipWithRespondent']
    # TODO: Replace with match-case in py 3.10
    if relationshipWithRespondent == 'father':
        return 'father', True
    elif relationshipWithRespondent == 'mother':
        return 'mother', True
    elif relationshipWithRespondent in ['child', 'brother', 'sister', 'sibling']:
        return 'child', False
    elif "inlaw" in relationshipWithRespondent.replace("-", "").lower():
        return 'in-law', False
    elif relationshipWithRespondent in ['', 'other']:
        return 'other', False
    return UNKNOWN_STRING, False


def init_respondent(beneficiary, parentFound):
    respondent = getMappedDict(config['respondentMapping'], beneficiary)
    respondent['familyRole'] = determine_respondent_role(
        respondent, parentFound)
    # no data regarding some of the respondent's field. use unknown
    respondent['disadvantaged'] = UNKNOWN_STRING
    respondent['prevYearTenth'] = UNKNOWN_STRING
    respondent['prevYearTwelfth'] = UNKNOWN_STRING
    respondent['tenthTopTen'] = UNKNOWN_STRING
    respondent['twelfthTopTen'] = UNKNOWN_STRING
    respondent['jobType'] = UNKNOWN_STRING
    respondent['tenthPercentageMarks'] = GetDBFloatString('-1')
    respondent['twelfthPercentageMarks'] = GetDBFloatString('-1')
    return respondent


def determine_respondent_role(respondent, parentFound):
    if parentFound:
        return 'child'
    elif respondent['gender'] == 'male':
        return 'father'
    elif respondent['gender'] == 'female':
        return 'mother'
    return UNKNOWN_STRING


def populate_pregnancy_status(family, respondent, beneficiary):
    # get the names of the pregnant women of the family from the pregnancy mapping
    pregnantWomenCombinedDict = getMappedDict(
        config['pregnancyMapping'], beneficiary)
    # current data has a provision of only two pregnant women, so pass two
    pregnantWomen = splitCombinedDict(pregnantWomenCombinedDict, 2)

    for woman in pregnantWomen:
        name = woman['name'].strip()
        if name == '':
            return
        fuzzyScore, index = fuzzy_matching(
            name, family['members'] + [respondent])
        if index >= 0 and index < (len(family['members']) - 1):
            family['members'][index]['pregnancy'] = 'yes'
        elif index == (len(family['members']) - 1):
            respondent['pregnancy'] = 'yes'
    for member in (family['members'] + [respondent]):
        if member['gender'] == 'male':
            member['pregnancy'] = 'no'
        elif 'pregnancy' not in member or member['pregnancy'] == '':
            member['pregnancy'] = UNKNOWN_STRING


def fuzzy_matching(name, members):
    fuzzyScore = -999
    index = -1
    for i, m in enumerate(members):
        memberName = m['name']
        if memberName == '':
            continue
        # using simple ratio for now, will tweak later if needed
        f = fuzz.ratio(name, memberName)
        if f > fuzzyScore:
            fuzzyScore = f
            index = i
    return fuzzyScore, index
