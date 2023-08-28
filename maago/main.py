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
    # '/proximity_score/bocw/json', app.views.ProximityScoreBOCWJSONView
)

if __name__ == "__main__":
    InitGlobals()
    app = web.application(urls, locals())
    app.run()
