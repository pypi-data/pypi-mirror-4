from elephunk.database import Row

class Activity(Row):

    @property
    def formatted_xact_start(self):
        if self.xact_start == None:
            return ""
        return self.xact_start.isoformat()
