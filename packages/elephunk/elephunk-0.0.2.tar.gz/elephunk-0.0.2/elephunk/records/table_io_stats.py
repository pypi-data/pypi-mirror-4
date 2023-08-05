from elephunk.database import Row

class TableIOStats(Row):

    @property
    def heap_blks_accessed(self):
        return (self.heap_blks_read or 0) + (self.heap_blks_hit or 0)

    @property
    def idx_blks_accessed(self):
        return (self.idx_blks_read or 0) + (self.idx_blks_hit or 0)

    @property
    def toast_blks_accessed(self):
        return (self.toast_blks_read or 0) + (self.toast_blks_hit or 0)

    @property
    def tidx_blks_accessed(self):
        return (self.tidx_blks_read or 0) + (self.tidx_blks_hit or 0)
