import web
import app.views

urls = (
    '/schemes', app.views.SchemeListView,
    '/proximity_score/csv', app.views.ProximityScoreCSV,
    '/proximity_score/json', app.views.ProximityScoreJSON
)

if __name__ == '__main__':
    app = web.application(urls, locals())
    app.run()
