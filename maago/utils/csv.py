import csv
import sys


class SimpleCSVLoader:
    # single header row
    def __init__(self, filename):
        try:
            f = open(filename, encoding='utf-8-sig')
            self.reader = csv.DictReader(f)
        except:
            print('cannot load beneficiary file: %s' %
                  filename, file=sys.stderr)
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
        self.reader = csv.DictReader(f, fieldnames=self.header)
        for x in self.reader:
            numHeader -= 1
            if numHeader == 0:
                break

    def __iter__(self):
        for x in self.reader:
            yield x


def getMappingFromCSVLoaderResponse(resp):
    retVal = {}
    for row in resp:
        retVal[row['src']] = {'dest': row['dest'], 'dataType': row['dataType']}
    return retVal
