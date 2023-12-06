"""
API Routes
"""

import datetime
import json
from app.perma_db import SingletonMySQLDB
from utils.exception_handler import ErrorCatcher
from utils.proximity_score import populateProximityScores
from utils.logger import logger
import web
from app.db import get_all_schemes, insert_scheme
from projects.cg_rte_plus.loader import CGRTEPlusLoader
from projects.bocw.loader import BOCWLoader


class BaseView:
    __metaclass__ = ErrorCatcher

    def _set_headers(self):
        """
        Used to set the headers for the response.
        """
        # web.header('Content-Type', 'application/json')
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Access-Control-Allow-Headers', '*')
        web.header('Access-Control-Allow-Credentials', 'true')

    def check_key(self, tenant: str):
        """
        Checks the api keys.
        Currently does not care about the tenant.
        @QUESTION: Should this have been a decorator?
        @TODO: Needs to be permission level too.
        """
        param = web.input()
        API_KEYS = SingletonMySQLDB.fetch_auth_key('')
        # TODO: Currently only sending keys. Send tuple instead
        if 'key' in param:
            if param.key in API_KEYS:
                # Check tenant
                return True
        return False

    def bad_response(self, code, message):
        """
        Generates the Error Response.
        """
        switcher = {
            400: web.BadRequest(message=message),
            401: web.Unauthorized(message=message)
        }
        logger.info(message)
        return switcher.get(code, web.BadRequest(message=message))
    
    def good_response(self, response, f):
        """
        Creates a log entry.
        Sets headers and jsonify the data before returning.
        """
        ct = datetime.datetime.now()
        message = "{}: 200 OK in {}".format(ct, f.__qualname__)
        logger.info(response)
        logger.info(message)
        self._set_headers()
        return json.dumps(response)
    
    def OPTIONS(self):
        return self.good_response({}, self.OPTIONS)


class SchemeListView(BaseView):
    """
    Handles addition and retrieval of schemes.
    Not in use right now.
    @QUESTION: Deprecate?
    """
    def GET(self):
        """
        Process GET requests on '/schemes' route.
        """
        if (not self.check_key('')):
            return self.bad_response(401, "Invalid Key")
        schemes = get_all_schemes()
        return self.good_response(schemes, self.GET)

    def POST(self):
        """
        Process POST requests on '/schemes' route.
        """
        if (not self.check_key('')):
            return self.bad_response(401, "Invalid Key")
        data = json.loads(web.data())
        insert_scheme(data)
        return self.good_response(data, self.POST)


class SchemeBulkAddView(BaseView):
    """
    Handles bulk addition for schemes.
    Not in use right now.
    @QUESTION: Deprecate?
    """
    def POST(self):
        """
        Process POST requests on '/schemes/bulk' route.
        """
        if (not self.check_key('')):
            return self.bad_response(401, "Invalid Key")
        data = json.loads(web.data())
        for s in data:
            insert_scheme(s)
        return self.good_response(data, self.POST)


class ProximityScoreCGRTEPlusJSONView(BaseView):
    """
    Handles proximity score checks for CG RTE+
    """
    def POST(self):
        """
        Process POST requests on 'proximity_score/cg_rte_plus/json' route.
        """
        if (not self.check_key('')):
            return self.bad_response(401, "Invalid Key")
        data = json.loads(web.data())
        if not data:
            jsonFile = open("projects/cg_rte_plus/config/input.json")
            data = json.load(jsonFile)
        loader = CGRTEPlusLoader()
        loader.load_schemes()
        loader.load_beneficiaries(data["beneficiaries"])
        schemeBeneficiaries = loader.get_beneficiary_scheme_mapping()
        loader.cleanup()
        return self.good_response(schemeBeneficiaries, self.POST)
    
    
class ProximityScoreBoCWJSONView(BaseView):
    """
    Handles proximity score checks for BoCW
    """
    def POST(self):
        """
        Process POST requests on 'proximity_score/bocw/json' route.
        """
        if (not self.check_key('')):
            return self.bad_response(401, "Invalid Key")
        data = json.loads(web.data())
        if not data:
            jsonFile = open("projects/bocw/config/input.json")
            data = json.load(jsonFile)
        loader = BOCWLoader()
        loader.load_schemes()
        loader.load_beneficiaries(data["beneficiaries"])
        schemeBeneficiaries = loader.get_beneficiary_scheme_mapping()
        loader.cleanup()
        return self.good_response(schemeBeneficiaries, self.POST)

