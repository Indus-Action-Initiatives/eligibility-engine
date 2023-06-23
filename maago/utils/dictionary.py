from utils import proximity_score

# fm##1$$job
INDIVIDUAL_SEPARATOR = "##"
ATTRIBUTE_SEPARATOR = "$$"
# We probably don't need this. TODO: Remove if necessary.
# We are doing this so that no data is missed if any of he property is missing
MAXIMUM_NUMBER_OF_FAMILY_MEMBERS = 6

def getMappedDict(headerMapping, srcDict):
    destDict = {}
    for key in headerMapping.keys():
        if key in srcDict.keys():
            # TODO: Use typecasting
            # HACK: using unknown value directly in case of empty string
            value = srcDict[key]
            dataType = headerMapping[key]['dataType']
            if value=='':
                if dataType in ['string', 'bool']:
                    value = proximity_score.UNKNOWN_STRING
                elif dataType=='number':
                    value = proximity_score.UNKNOWN_NUMBER
                elif dataType=='date':
                    value = proximity_score.UNKNOWN_DATE.strftime("%d-%m-%Y")
            destDict[headerMapping[key]["dest"]] = value
    return destDict


def splitCombinedDict(combinedDict, numberOfSplits=MAXIMUM_NUMBER_OF_FAMILY_MEMBERS):
    splits = []

    for i in range(numberOfSplits):
        splits.append({})

    for key, value in combinedDict.items():
        idPlusAttribute = key.split(INDIVIDUAL_SEPARATOR)[1]
        idPlusAttribute = idPlusAttribute.split(ATTRIBUTE_SEPARATOR)
        id = int(idPlusAttribute[0]) - 1
        attribute = idPlusAttribute[1]
        splits[id][attribute] = value

    return splits
