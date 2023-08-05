from elephunk.database import Row

class Database(Row):

    @property
    def stats_reset_iso(self):
        return self.stats_reset.isoformat() if self.stats_reset else "never"
