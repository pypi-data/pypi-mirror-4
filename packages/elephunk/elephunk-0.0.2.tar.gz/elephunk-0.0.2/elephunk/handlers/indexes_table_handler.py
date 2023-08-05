from tornado import gen
from tornado.web import asynchronous
from base_handler import BaseHandler

class IndexesTableHandler(BaseHandler):

    @asynchronous
    @gen.engine
    def get(self, datid, relid):
        database_name = yield gen.Task(self.client_for('postgres').select_scalar, "SELECT datname FROM pg_stat_database WHERE datid = %s", (datid,))
        table = yield gen.Task(self.client_for(database_name).select_one, "SELECT * FROM pg_stat_user_tables WHERE relid = %s", (relid,))
        indexes = yield gen.Task(self.client_for(database_name).select_all, self._index_query(), (relid,))
        self.render('indexes/table.html', datid=datid, database_name=database_name, table=table, indexes=indexes)

    def _index_query(self):
        return """
            SELECT stats.*,
                   idx.*,
                   pg_size_pretty(pg_relation_size(stats.indexrelid)) as idx_size
            FROM pg_stat_user_indexes stats
            INNER JOIN pg_index idx ON idx.indexrelid = stats.indexrelid
            WHERE stats.relid = %s
        """
