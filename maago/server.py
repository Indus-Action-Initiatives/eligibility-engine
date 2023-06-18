import web
import csv

urls = (
    '/', 'Index',
    '/load', 'LoadFile'
)

render = web.template.render("maago/templates")


class Index:
    def GET(self):
        return '<h1>Generic Get</h1>'


class LoadFile:
    def GET(self, file=None):
        return render.upload_form(file)

    def POST(self):
        request = web.input(csvFile={})
        # web.debug(request['csvFile'].filename)
        # web.debug(request['csvFile'].value)
        # TODO: Encoding of the file is messed up. FIXME
        file = request['csvFile'].file.read()
        web.debug(file)
        table = [[]]
        raise web.seeother('load', file)


if __name__ == '__main__':
    app = web.application(urls, locals())
    app.run()
