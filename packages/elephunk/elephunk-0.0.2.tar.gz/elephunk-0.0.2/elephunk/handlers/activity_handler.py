from tornado import gen
from tornado.web import asynchronous
from base_handler import BaseHandler
from elephunk.records.activity import Activity

class ActivityHandler(BaseHandler):
    @asynchronous
    @gen.engine
    def get(self):
        rows = yield gen.Task(self.client_for('postgres').select_all, "SELECT * FROM pg_stat_activity", record=Activity)
        self.render("activity/index.html", connections=rows)
