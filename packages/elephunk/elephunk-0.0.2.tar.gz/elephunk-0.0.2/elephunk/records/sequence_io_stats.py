from elephunk.database import Row

class SequenceIOStats(Row):

    @property
    def blks_accessed(self):
        return (self.blks_read or 0) + (self.blks_hit or 0)
