from tornado.web import UIModule

class CurrentServer(UIModule):
    def render(self):
        selected_server = self.handler.selected_server()
        servers = self.handler.application.db.server_names()
        return self.render_string("ui_modules/current_server.html", servers=servers, selected_server=selected_server)


