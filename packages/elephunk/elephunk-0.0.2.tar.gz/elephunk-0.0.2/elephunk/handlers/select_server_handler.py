from base_handler import BaseHandler

class SelectServerHandler(BaseHandler):
    def post(self):
        self.set_cookie("selected-server", self.get_argument("server"))
        self.redirect(self.request.headers['Referer'])

