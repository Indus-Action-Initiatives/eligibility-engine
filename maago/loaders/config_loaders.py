from utils.csv import CSVLoader, getMappingFromCSVLoaderResponse


familyMapping = getMappingFromCSVLoaderResponse(
    CSVLoader('config/familyMapping.csv'))
# familyJSONMapping = getMappingFromCSVLoaderResponse(
#     CSVLoader('config/familyJSONMapping.csv'))
locationMapping = getMappingFromCSVLoaderResponse(
    CSVLoader('config/locationMapping.csv'))
respondentMapping = getMappingFromCSVLoaderResponse(
    CSVLoader('config/respondentMapping.csv'))
familyMembersMapping = getMappingFromCSVLoaderResponse(
    CSVLoader('config/familyMembersMapping.csv'))
pregnancyMapping = getMappingFromCSVLoaderResponse(
    CSVLoader('config/pregnancyMapping.csv'))


def get_config_mappings():
    config = {
        "familyMapping": familyMapping,
        # "familyJSONMapping": familyJSONMapping,
        "locationMapping": locationMapping,
        "respondentMapping": respondentMapping,
        "familyMembersMapping": familyMembersMapping,
        "pregnancyMapping": pregnancyMapping, }
    return config
