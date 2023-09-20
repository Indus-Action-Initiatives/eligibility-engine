import datetime
import json
from utils.exception_handler import ErrorCatcher
from utils.proximity_score import populateProximityScores
import web
from app.db import get_all_schemes, insert_scheme
from projects.cg_rte_plus.loader import CGRTEPlusLoader
from projects.bocw.loader import BOCWLoader


class SchemeListView:
    __metaclass__ = ErrorCatcher
    def GET(self):
        schemes = get_all_schemes()
        return json.dumps(schemes)

    def POST(self):
        data = json.loads(web.data())
        insert_scheme(data)
        return json.dumps(data)


class SchemeBulkAddView:
    __metaclass__ = ErrorCatcher
    def POST(self):
        data = json.loads(web.data())
        for s in data:
            insert_scheme(s)
        return json.dumps(data)


# class ProximityScoreCSV:
#     def GET(self):
#         return '<h1>Test Get</h1>'

#     def POST(self):
#         data = json.loads(web.data())
#         csv_content = data['content']
#         csv_file = io.StringIO(csv_content)
#         csv_reader = csv.DictReader(csv_file)

#         schemes = get_all_schemes()
#         return web.seeother('proximity_score/csv')


class ProximityScoreCGRTEPlusJSONView(metaclass=ErrorCatcher):
    def setHeaders(self):
        # web.header('Content-Type', 'application/json')
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Access-Control-Allow-Credentials', 'true')

    def POST(self):
        data = json.loads(web.data())
        if not data:
            jsonFile = open("projects/cg_rte_plus/config/input.json")
            data = json.load(jsonFile)

        loader = CGRTEPlusLoader()
        loader.load_schemes()
        loader.load_beneficiaries(data["beneficiaries"])
        schemeBeneficiaries = loader.get_beneficiary_scheme_mapping()
        # schemeBeneficiaries = {}
        # populateProximityScores(
        #     schemeBeneficiaries, rows, orderedColumns, criteriaColumns
        # )
        # web.debug(schemeBeneficiaries)
        loader.cleanup()
        ct = datetime.datetime.now()
        response = "{}: 200 OK in ProximityScoreCGRTEPlusJSONView.POST".format(ct)
        print(response)
        self.setHeaders()
        return json.dumps(schemeBeneficiaries)
    
    def OPTIONS(self):
        self.setHeaders()
        response = "{}: 200 OK in ProximityScoreCGRTEPlusJSONView.OPTIONS".format(ct)
        print(response)
        return json.dumps({})


class ProximityScoreBoCWJSONView(metaclass=ErrorCatcher):
    def setHeaders(self):
        # web.header('Content-Type', 'application/json')
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Access-Control-Allow-Headers', '*')
        web.header('Access-Control-Allow-Credentials', 'true')

    def POST(self):
        data = json.loads(web.data())
        if not data:
            jsonFile = open("projects/bocw/config/input.json")
            data = json.load(jsonFile)

        loader = BOCWLoader()
        loader.load_schemes()
        loader.load_beneficiaries(data["beneficiaries"])
        schemeBeneficiaries = loader.get_beneficiary_scheme_mapping()
        # schemeBeneficiaries = {}
        # populateProximityScores(
        #     schemeBeneficiaries, rows, orderedColumns, criteriaColumns
        # )
        # web.debug(schemeBeneficiaries)
        loader.cleanup()
        ct = datetime.datetime.now()
        response = "{}: 200 OK in ProximityScoreBoCWJSONView.POST".format(ct)
        print(response)
        self.setHeaders()
        return json.dumps(schemeBeneficiaries)
    
    def OPTIONS(self):
        self.setHeaders()
        response = "{}: 200 OK in ProximityScoreCGRTEPlusJSONView.OPTIONS".format(ct)
        print(response)
        return json.dumps({})
