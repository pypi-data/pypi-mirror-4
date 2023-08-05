from tornado import gen
from tornado.web import asynchronous
from base_handler import BaseHandler

class BloatServerHandler(BaseHandler):

    @asynchronous
    @gen.engine
    def get(self):
        rows = yield gen.Task(self.client_for('postgres').select_all, "SELECT *, pg_size_pretty(pg_database_size(datid)) AS size FROM pg_stat_database")
        self.render("bloat/server.html", databases=rows)
