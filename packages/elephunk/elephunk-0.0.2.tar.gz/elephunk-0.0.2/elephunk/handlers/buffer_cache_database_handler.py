from tornado import gen
from tornado.web import asynchronous
from base_handler import BaseHandler
from elephunk.records.table_io_stats import TableIOStats
from elephunk.records.index_io_stats import IndexIOStats
from elephunk.records.sequence_io_stats import SequenceIOStats

class BufferCacheDatabaseHandler(BaseHandler):

    @asynchronous
    @gen.engine
    def get(self, datid):
        database_name = yield gen.Task(self.client_for('postgres').select_scalar, "SELECT datname FROM pg_stat_database WHERE datid = %s", (datid,))
        tables = yield gen.Task(self.client_for(database_name).select_all, "SELECT * FROM pg_statio_user_tables ORDER BY schemaname, relname", record=TableIOStats)
        indexes = yield gen.Task(self.client_for(database_name).select_all, "SELECT * FROM pg_statio_user_indexes ORDER BY schemaname, relname, indexrelname", record=IndexIOStats)
        sequences = yield gen.Task(self.client_for(database_name).select_all, "SELECT * FROM pg_statio_user_sequences ORDER BY relname", record=SequenceIOStats)
        self.render('buffer_cache/database.html', database_name=database_name, tables=tables, indexes=indexes, sequences=sequences)
