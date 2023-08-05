from tornado import gen
from tornado.escape import json_encode
from tornado.web import asynchronous
from base_handler import BaseHandler

class IndexesDatabaseHandler(BaseHandler):

    @asynchronous
    @gen.engine
    def get(self, datid):
        database_name = yield gen.Task(self.client_for('postgres').select_scalar, "SELECT datname FROM pg_stat_database WHERE datid = %s", (datid,))
        tables = yield gen.Task(self.client_for(database_name).select_all, "SELECT * FROM pg_stat_user_tables")
        indexes = yield gen.Task(self.client_for(database_name).select_all, self._index_query())
        index_data = IndexesDatabaseHandler.build_json(database_name, tables, indexes)
        self.render('indexes/database.html', datid=datid, database_name=database_name, index_data=index_data)

    def _index_query(self):
        return """
            SELECT stats.*,
                   idx.*,
                   pg_size_pretty(pg_relation_size(stats.indexrelid)) as idx_size
            FROM pg_stat_user_indexes stats
            INNER JOIN pg_index idx ON idx.indexrelid = stats.indexrelid
        """

    @staticmethod
    def build_json(database, tables, indexes):
        grouped_indexes = reduce(IndexesDatabaseHandler._group_by_table, indexes, {})
        children = [IndexesDatabaseHandler.map_table(table, grouped_indexes) for table in tables]
        return json_encode(dict(name=database, children=children))

    @staticmethod
    def map_index(index):
        name = "%s.%s.%s" % (index.schemaname, index.relname, index.indexrelname)
        return dict(name=name, value=index.idx_scan, scans=index.idx_scan, tuples=(index.idx_tup_read + index.idx_tup_fetch), isIndex=True, isUnique=index.indisunique)

    @staticmethod
    def map_table(table, grouped_indexes):
        name = "%s.%s.%s" % (table.schemaname, table.relname, 'unindexed')
        children = [dict(name=name, value=table.seq_scan, scans=table.seq_scan, tuples=table.seq_tup_read, isIndex=False)]

        if table.relid in grouped_indexes:
            children += grouped_indexes[table.relid]

        return dict(name="%s.%s"%(table.schemaname, table.relname), children=children)

    @staticmethod
    def _group_by_table(groups, index):
        if index.relid in groups:
            groups[index.relid].append(IndexesDatabaseHandler.map_index(index))
        else:
            groups[index.relid] = [IndexesDatabaseHandler.map_index(index)]

        return groups
