from middleware.logger import Log
import web
import app.views
from utils.proximity_score import InitGlobals
from utils.logger import logger

urls = (
    "/schemes",
    app.views.SchemeListView,
    "/schemes/bulk",
    app.views.SchemeBulkAddView,
    "/proximity_score/cg_rte_plus/json",
    app.views.ProximityScoreCGRTEPlusJSONView,
    "/proximity_score/bocw/json",
    app.views.ProximityScoreBoCWJSONView,
    "/proximity_score/c2p/json",
    app.views.ProximityScoreC2PJSONView,
)

app = web.application(urls, locals())
wsgiapp = app.wsgifunc(Log)

if __name__ == "__main__":
    InitGlobals()
    app.run(Log)
    logger.info("server started at port: 8080")
