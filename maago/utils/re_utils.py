import re


def getColumnsFromCriterion(criterion: str) -> list:
    return re.findall('fm\.\w+|f\.\w+', criterion)


def getOrderedColumnNamesFromTheSelectClause(fromClause):
    return re.findall(' as \'?([\\w.]+)\'?', fromClause)
