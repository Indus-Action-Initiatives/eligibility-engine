import web
import app.views

urls = (
    '/schemes', app.views.SchemeListView,
    '/schemes/bulk', app.views.SchemeBulkAddView,
    # '/proximity_score/csv', app.views.ProximityScoreCSV,
    '/proximity_score/json', app.views.ProximityScoreJSONView
)

if __name__ == '__main__':
    app = web.application(urls, locals())
    app.run()
