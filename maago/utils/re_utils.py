import re


def getColumnsFromCriterion(criterion: str) -> list:
    return re.findall("fm\.\w+|f\.\w+", criterion)


def getOrderedColumnNamesFromTheSelectClause(fromClause):
    columnNames = re.findall(" as '([\\w.]+)'", fromClause)
    uniqueColumnNames = []
    for c in columnNames:
        if c not in uniqueColumnNames:
            uniqueColumnNames.append(c)

    return uniqueColumnNames
