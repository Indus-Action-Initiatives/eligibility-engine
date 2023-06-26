import json
from loaders.beneficiary_loaders import load_beneficiaries_to_db
from loaders.beneficiary_scheme_mapping import get_beneficiary_scheme_mapping
from utils.proximity_score import populateProximityScores
import web
import io
import csv
from app.db import get_all_schemes, insert_scheme


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


class ProximityScoreJSONView:
    # def GET(self, res={}):
    #     return json.dumps(res)

    def POST(self):
        data = json.loads(web.data())
        if not data:
            jsonFile = open("maago/input.json")
            data = json.load(jsonFile)
        load_beneficiaries_to_db(data['beneficiaries'])
        rows, orderedColumns, criteriaColumns = get_beneficiary_scheme_mapping()
        schemeBeneficiaries = {}
        # populate respective fields for each beneficiary and calculate the proximity scores for each one of them
        populateProximityScores(schemeBeneficiaries, rows,
                                orderedColumns, criteriaColumns)
        web.debug(schemeBeneficiaries)
        return json.dumps(schemeBeneficiaries)
