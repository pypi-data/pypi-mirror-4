from elephunk.database import Row

class IndexIOStats(Row):

    @property
    def idx_blks_accessed(self):
        return (self.idx_blks_read or 0) + (self.idx_blks_hit or 0)
