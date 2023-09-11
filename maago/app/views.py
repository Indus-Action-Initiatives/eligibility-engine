import json
from utils.proximity_score import populateProximityScores
import web
from app.db import get_all_schemes, insert_scheme
from projects.cg_rte_plus.loader import CGRTEPlusLoader
from projects.bocw.loader import BOCWLoader


class SchemeListView:
    def GET(self):
        schemes = get_all_schemes()
        return json.dumps(schemes)

    def POST(self):
        data = json.loads(web.data())
        insert_scheme(data)
        return json.dumps(data)


class SchemeBulkAddView:
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


class ProximityScoreCGRTEPlusJSONView:
    def POST(self):
        data = json.loads(web.data())
        if not data:
            jsonFile = open("maago/projects/cg_rte_plus/config/input.json")
            data = json.load(jsonFile)

        loader = CGRTEPlusLoader()
        loader.load_schemes()
        loader.load_beneficiaries(data["beneficiaries"])
        schemeBeneficiaries = loader.get_beneficiary_scheme_mapping()
        # schemeBeneficiaries = {}
        # populateProximityScores(
        #     schemeBeneficiaries, rows, orderedColumns, criteriaColumns
        # )
        web.debug(schemeBeneficiaries)
        loader.cleanup()
        return json.dumps(schemeBeneficiaries)


class ProximityScoreBoCWJSONView:
    def POST(self):
        data = json.loads(web.data())
        if not data:
            jsonFile = open("maago/projects/bocw/config/input.json")
            data = json.load(jsonFile)

        loader = BOCWLoader()
        loader.load_schemes()
        loader.load_beneficiaries(data["beneficiaries"])
        schemeBeneficiaries = loader.get_beneficiary_scheme_mapping()
        # schemeBeneficiaries = {}
        # populateProximityScores(
        #     schemeBeneficiaries, rows, orderedColumns, criteriaColumns
        # )
        web.debug(schemeBeneficiaries)
        loader.cleanup()
        return json.dumps(schemeBeneficiaries)
