from base_handler import BaseHandler

class RootHandler(BaseHandler):
    def get(self):
        self.render("index.html")
