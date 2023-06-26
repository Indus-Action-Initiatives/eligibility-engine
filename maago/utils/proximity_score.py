from datetime import datetime


UNKNOWN_SCORE = 0.001
UNKNOWN_STRING = 'unknown'
UNKNOWN_NUMBER = -111111
UNKNOWN_DATE = datetime.strptime('01-01-1800', '%d-%m-%Y')
PROXIMITY_SCORE_KEY = 'proximity_score'


def calculateProximityScore(rowValues, criteriaColumns):
    unknowns = [UNKNOWN_STRING, UNKNOWN_NUMBER, UNKNOWN_DATE, None]
    proximityScore = 0
    totalScore = 0
    criteriaKeys = list(filter(lambda k: 'criteria' in k, rowValues.keys()))
    for k in criteriaKeys:
        if k == 'main_criteria':
            continue
        if rowValues[k] == 1:
            totalScore += 1
        else:
            # check for unknown values and factor those in
            # right now only A is supported, (A AND B) is not
            # stupid!
            #
            # we do not support any ORs right now, so just bailing out whenever
            # any known failing criteria is found
            kColumns = criteriaColumns[k]
            guarenteedFailingCriteriaFound = False
            for c in kColumns:
                if rowValues[c] in unknowns:
                    totalScore += UNKNOWN_SCORE
                    # this breaks my heart as well
                    break
                else:
                    guarenteedFailingCriteriaFound = True
                    break
            if guarenteedFailingCriteriaFound:
                totalScore = 0
                break
    proximityScore = totalScore/(len(criteriaKeys) - 1)

    return proximityScore


def populateProximityScores(schemeBeneficiaries, rows, orderedColumnNames, criteriaColumns):
    for row in rows:
        rowValues = row
        # for i, c in enumerate(orderedColumnNames):
        #     rowValues[c] = row[i]

        beneficiaryKey = '%s__%s' % (rowValues['f.id'], rowValues['fm.id'])
        schemeName = rowValues['scheme_name']
        beneficiary = {}
        if beneficiaryKey in schemeBeneficiaries:
            beneficiary = schemeBeneficiaries[beneficiaryKey]
        for i, (key, v) in enumerate(row.items()):
            if 'criteria' not in key:
                beneficiary[key] = row[key]
            else:
                # TODO: Add description of the criteria as well.
                beneficiary['%s__%s' % (schemeName, key)] = row[key]
        if rowValues['main_criteria'] == 1:
            beneficiary['%s__%s' % (schemeName, PROXIMITY_SCORE_KEY)] = 1
        else:
            beneficiary['%s__%s' % (schemeName, PROXIMITY_SCORE_KEY)] = calculateProximityScore(
                rowValues, criteriaColumns)
        schemeBeneficiaries[beneficiaryKey] = beneficiary

    return
