from loaders.scheme_loaders import LoadSchemes, SchemeName, getCriteriaTokensFromInclusionCriteria
from utils.db import GetDBConnection
from utils.normalization import normalizeString
from utils.proximity_score import populateProximityScores
from utils.re_utils import getColumnsFromCriterion, getOrderedColumnNamesFromTheSelectClause


def GetBeneficiarySchemesMapping():
    schemes = LoadSchemes()
    dbConnection = GetDBConnection()
    cursor = dbConnection.cursor()
    schemeBeneficiaries = {}
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
            criteriaStrings.append(
                'CASE WHEN %s THEN 1 ELSE 0 END as criteria%d' % (c, i))
        mainCriteriaString = '(CASE WHEN %s THEN 1 ELSE 0 END) as main_criteria' % inclusionCriteria
        fromClause = 'FROM families as f INNER JOIN family_members as fm ON f.id = fm.family_id'
        selectClause = 'SELECT \'%s\' as scheme_name, f.id as \'f.id\', fm.id as \'fm.id\', ' % s['name'] + ', '.join(
            ['%s as \'%s\'' % (c, c) for c in columns]) + ', ' + ', '.join(criteriaStrings) + ', ' + mainCriteriaString
        eligibilityQuery = selectClause + ' ' + fromClause

        # get values for each part of the select clause
        orderedColumnNames = getOrderedColumnNamesFromTheSelectClause(
            selectClause)

        cursor.execute(eligibilityQuery)
        rows = cursor.fetchall()

        # populate respective fields for each beneficiary and calculate the proximity scores for each one of them
        populateProximityScores(schemeBeneficiaries,
                                rows, orderedColumnNames, criteriaColumns)

    print(schemeBeneficiaries)

    cursor.close()
    dbConnection.close()

    return schemeBeneficiaries


def match(beneficiary, scheme):
    print('chosen scheme: %s' % SchemeName(scheme))
    print('criteria:')
    for k, v in scheme.items():
        if v.strip():
            print('    %s = %s' % (normalizeString(k), normalizeString(v)))
    print('beneficiary attributes (total %d):' % len(beneficiary))
    for k, v in beneficiary.items():
        print('        %s' % (normalizeString(k)))
    for k, v in beneficiary.items():
        if v.strip():
            print('    %s = %s' % (normalizeString(k), normalizeString(v)))