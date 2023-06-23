import json
from loaders.beneficiary_loaders import load_beneficiaries_to_db
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


class ProximityScoreCSV:
    def GET(self):
        return '<h1>Test Get</h1>'

    def POST(self):
        data = json.loads(web.data())
        csv_content = data['content']
        csv_file = io.StringIO(csv_content)
        csv_reader = csv.DictReader(csv_file)

        schemes = get_all_schemes()
        return web.seeother('proximity_score/csv')


class ProximityScoreJSON:
    def GET(self):
        return '<h1>Test Get</h1>'

    def POST(self):
        jsonFile = open("maago/input.json")
        data = json.load(jsonFile)
        web.debug(load_beneficiaries_to_db(data['beneficiaries']))
        return web.seeother('/proximity_score/json')
