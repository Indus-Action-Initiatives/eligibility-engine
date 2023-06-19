from utils.csv import CSVLoader


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


def LoadSchemes() -> CSVLoader:
    schemes = CSVLoader('maago/config/schemes.csv')
    return schemes


def SchemeName(scheme):
    return ' : '.join([scheme[State], scheme[Sector], scheme[SubScheme], scheme[IDiSchemeSubDiv]])


def getCriteriaTokensFromInclusionCriteria(criteria: str):
    # Assumptions:
    # 1. Each criterion is enclosed in a pair of parenthesis
    # 2. In case of nested parenthesis, the inner parenthesis will be ignored
    # 3. Criteria are connected with only AND, ORs are not allowed as connectors
    # 4. ORs are always inside the token, i.e. within the parenthesis
    tokens: list[str] = []

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
