from middleware.logger import Log
import web
import app.views
from utils.proximity_score import InitGlobals

urls = (
    "/schemes",
    app.views.SchemeListView,
    "/schemes/bulk",
    app.views.SchemeBulkAddView,
    # '/proximity_score/csv', app.views.ProximityScoreCSV,
    "/proximity_score/cg_rte_plus/json",
    app.views.ProximityScoreCGRTEPlusJSONView,
    "/proximity_score/bocw/json",
    app.views.ProximityScoreBoCWJSONView,
)

app = web.application(urls, locals())
wsgiapp = app.wsgifunc()

if __name__ == "__main__":
    InitGlobals()
    app.run(Log)
