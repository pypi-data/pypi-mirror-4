import logging
import tornado.web

class BaseHandler(tornado.web.RequestHandler):

    def client_for(self, database):
        return self.application.db.client(self.selected_server(), database)

    def selected_server(self):
        server = self.get_cookie("selected-server") or self.application.db.server_names()[0]
        if self.get_cookie("selected-server") == None:
            self.set_cookie("selected-server", server)

        return server

