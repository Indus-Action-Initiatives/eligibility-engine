from utils.csv import CSVLoader, getMappingFromCSVLoaderResponse


familyMapping = getMappingFromCSVLoaderResponse(
    CSVLoader('maago/config/familyMapping.csv'))
# familyJSONMapping = getMappingFromCSVLoaderResponse(
#     CSVLoader('maago/config/familyJSONMapping.csv'))
locationMapping = getMappingFromCSVLoaderResponse(
    CSVLoader('maago/config/locationMapping.csv'))
respondentMapping = getMappingFromCSVLoaderResponse(
    CSVLoader('maago/config/respondentMapping.csv'))
familyMembersMapping = getMappingFromCSVLoaderResponse(
    CSVLoader('maago/config/familyMembersMapping.csv'))
pregnancyMapping = getMappingFromCSVLoaderResponse(
    CSVLoader('maago/config/pregnancyMapping.csv'))


def get_config_mappings():
    config = {
        "familyMapping": familyMapping,
        # "familyJSONMapping": familyJSONMapping,
        "locationMapping": locationMapping,
        "respondentMapping": respondentMapping,
        "familyMembersMapping": familyMembersMapping,
        "pregnancyMapping": pregnancyMapping, }
    return config
