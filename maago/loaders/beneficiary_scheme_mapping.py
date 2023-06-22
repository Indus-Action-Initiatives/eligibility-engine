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
        auxilliaryColumns = {}
        acKeysFromScheme = list(filter(lambda k: 'auxilliary' in k, s.keys()))
        for c in acKeysFromScheme:
            if s[c] == '':
                continue
            key = c.split("_")[1]            
            auxilliaryColumns[key] = s[c]
        inclusionCriteria = s['inclusion_criteria']
        criteria = getCriteriaTokensFromInclusionCriteria(inclusionCriteria)
        # TODO: Add exclusion criteria

        # get column from the criteria
        criteriaColumns = {}
        for i, c in enumerate(criteria):
            criteriaColumns['criteria%d' % i] = getColumnsFromCriterion(c)       

        criteriaStrings = []
        for i, c in enumerate(criteria):
            criteriaStrings.append(
                'CASE WHEN %s THEN 1 ELSE 0 END as `criteria%d`' % (c, i))
        mainCriteriaString = '(CASE WHEN %s THEN 1 ELSE 0 END) as `main_criteria`' % inclusionCriteria

        # from clause
        fromClause = 'FROM families as f INNER JOIN family_members as fm ON f.id = fm.family_id'

        # TODO: This is ugly, bad, nasty. Need to do a better job with this.
        # construct select clause
        selectClause = """SELECT \'%s\' as `scheme_name`,
            f.id as `f.id`, f.caste as `f.caste`, f.caste_category as `f.caste_category`, f.pr_of_cg as `f.pr_of_cg`, 
            f.has_residence_certificate as `f.has_residency_certificate`, f.ration_card_type as `f.ration_card_type`,
            f.ptgo_or_pvtg as `f.ptgo_or_pvtg`, f.are_forest_dwellers as `f.are_forest_dwellers`, f.has_phone as `f.has_phone`,
            f.has_neighbourhood_phone_number as `f.has_neighbourhood_phone_number`,
            fm.id as `fm.id`, fm.name as `fm.name`, fm.dob as `fm.dob`, fm.gender as `fm.gender`, fm.family_role as `fm.family_role`, fm.disadvantaged as `fm.disadvantaged`,
            fm.job as `fm.job`, fm.job_type as `fm.job_type`, fm.in_educational_institute as `fm.in_educational_institute`, fm.education_level as `fm.education_level`,
            fm.prev_year_tenth as `fm.prev_year_tenth`, fm.prev_year_twelfth as `fm.prev_year_twelfth`, fm.tenth_percentage_marks as `fm.tenth_percentage_marks`,
            fm.twelfth_percentage_marks as `fm.twelfth_percentage_marks`, fm.tenth_top_ten as `fm.tenth_top_ten`, fm.twelfth_top_ten as `fm.twelfth_top_ten`,
            fm.has_bocw_card as `fm.has_bocw_card`, fm.bocw_card_issue_date as `fm.bocw_card_issue_date`, fm.has_uow_card as `fm.has_uow_card`, fm.uow_card_issue_date as `fm.uow_card_issue_date`,
            fm.pregnancy as `fm.pregnancy`,          
            """ % s['name'] + ', '.join(['(%s) as `%s`' % (auxilliaryColumns[k], k) for k in auxilliaryColumns])
        
        # get values for each part of the select clause
        orderedColumnNames = getOrderedColumnNamesFromTheSelectClause(
            selectClause)
        
        # if auxilliary columns wrap the main query with a CTE
        if len(auxilliaryColumns) > 0:            
            selectClause = 'WITH cte_query AS (%s) SELECT ' % (selectClause + ' ' + fromClause) + ', '.join(['`%s` as \'%s\'' % (c, c) for c in orderedColumnNames])
            fromClause = 'FROM cte_query'
            # TODO: quote the columns in where clause in case of auxilliary columns

        selectClause = selectClause + (', ' if len(auxilliaryColumns) > 0 else '') + ', '.join(criteriaStrings) + ', ' + mainCriteriaString
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
