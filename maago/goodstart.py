#!/usr/bin/env python
#
# Angshuman Guha
# angshuman.guha@gmail.com

import csv
import random
import sys

class SimpleCSVLoader:
    # single header row
    def __init__(self, filename):
        try:
            f = open(filename, encoding='utf-8-sig')
            self.reader = csv.DictReader(f)
        except:
            print('cannot load beneficiary file: %s' % filename, file=sys.stderr)
            raise
    def __iter__(self):
        for x in self.reader:
            yield x

class CSVLoader:
    def __init__(self, filename, numHeader=1, useLastHeader=True):
        assert numHeader >= 1
        headers = []
        try:
            f = open(filename, encoding='utf-8-sig')
            reader = csv.reader(f)
        except:
            print('cannot load CSV file: %s' % filename, file=sys.stderr)
            raise
        for i in range(numHeader):
            headers.append(reader.__next__())
        self.header = []
        for i in range(len(headers[0])):
            tmp = []
            for header in headers:
                h = header[i].strip()
                if h:
                    tmp.append(h)
            if useLastHeader:
                self.header.append(tmp[-1])
            else:
                self.header.append(' '.join(tmp))
        f.close()
        f = open(filename, encoding='utf-8-sig')
        self.reader = csv.DictReader(f, fieldnames = self.header)
        for x in self.reader:
            numHeader -= 1
            if numHeader == 0:
                break
    def __iter__(self):
        for x in self.reader:
            yield x

State = 'State'
Sector = 'Sector'
Scheme = 'Scheme'
SubScheme = 'Sub-Scheme'
IDiSchemeSubDiv = 'IDi scheme sub-divisions'

def LoadSchemes():
    schemes = []
    n = 0
    for scheme in CSVLoader('benefitsCG.csv', numHeader=2):
        n += 1
        if (scheme[State] == 'Chhattisgarh'
          and scheme[Sector] == 'Right to Livelihood'
          and scheme[Scheme] == 'BoCW'
          and (scheme[SubScheme] == 'Noni Sashaktikaran Scheme'
               or scheme[SubScheme] == 'Mini Mata Mahtari Jatan Yojna'
               or scheme[SubScheme] == 'Chief Minister Shramik Tool Assistance Scheme'
               or scheme[SubScheme] == 'Naunihal Scholarship Scheme'
               or (scheme[SubScheme] == 'Meritorious Student / Student Education Promotion Scheme'
                    and scheme[IDiSchemeSubDiv] == 'B')
               or (scheme[SubScheme] == 'Construction Workers Permanent Disability and Accidental Death Pension Scheme'
                    and scheme[IDiSchemeSubDiv] == 'B'))):
              schemes.append(scheme)
        elif (scheme[State] == 'Chhattisgarh'
          and scheme[Sector] == 'Right to Livelihood'
          and scheme[Scheme] == 'UoW'
          and scheme[SubScheme] == 'Chief Minister Unorganized Workers Cycle Assistance Scheme'):
              schemes.append(scheme)
    print('considering %d schemas out of %d' % (len(schemes), n))
    return schemes

def SchemeName(scheme):
    return ' : '.join([scheme[State], scheme[Sector], scheme[SubScheme], scheme[IDiSchemeSubDiv]])

def normalizeString(s):
    return ' '.join(s.split())

def match(beneficiary, scheme):
    print('chosen scheme: %s' % SchemeName(scheme))
    print('criteria:')
    for k, v in scheme.items():
        if v.strip():
            print('    %s = %s' % (normalizeString(k), normalizeString(v)))
    print('beneficiary attributes:')
    for k, v in beneficiary.items():
        if v.strip():
            print('    %s = %s' % (normalizeString(k), normalizeString(v)))

def main():
    schemes = LoadSchemes()
    beneficiaries = []
    for beneficiary in CSVLoader('survey.csv'):
        beneficiaries.append(beneficiary)
    print('%d beneficiaries' % len(beneficiaries))
    # preprocess the beneficiary data
    scheme = random.choice(schemes)
    beneficiary = random.choice(beneficiaries)
    match(beneficiary, scheme)
    return 0

if __name__ == '__main__':
    sys.exit(main())
