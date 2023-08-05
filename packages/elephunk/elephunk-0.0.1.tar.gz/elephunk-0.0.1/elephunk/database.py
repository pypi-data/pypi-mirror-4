from urlparse import urlparse
from momoko.clients import AsyncClient

class Row:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class Database():
    def __init__(self, client):
        self.client = client

    def select_all(self, operation, parameters=(), record=Row, callback=None):
        self.client.execute(operation, parameters, callback = lambda cursor: callback(self._map_cursor(cursor, record)))

    def select_one(self, operation, parameters=(), record=Row, callback=None):
        self.client.execute(operation, parameters, callback = lambda cursor: callback(self._first_entry(cursor, record)))

    def select_scalar(self, operation, parameters=(), callback=None):
        self.client.execute(operation, parameters, callback = lambda cursor: callback(self._single_entry(cursor)))

    def _first_entry(self, cursor, record):
        if cursor.rowcount == 0:
            return None
        return self._map_cursor(cursor, record)[0]

    def _map_cursor(self, cursor, record):
        names = [x[0] for x in cursor.description]
        return [record(**dict(zip(names, row))) for row in cursor.fetchall()]

    def _single_entry(self, cursor):
        if cursor.rowcount == 0:
            return None
        return cursor.fetchall()[0][0]

class DatabaseClients:
    def __init__(self, servers, client_factory=AsyncClient):
        self._servers = servers
        self._client_factory = client_factory
        self._clients = {}

    def client(self, server_name, database_name):
        identifier = (server_name, database_name)
        if identifier not in self._clients:
            self._clients[identifier] = self._build_client(server_name, database_name)

        return self._clients[identifier]

    def close(self):
        for client in self._clients.itervalues():
            client.close()

    def server_names(self):
        return sorted(self._servers.keys())

    def _build_client(self, server_name, database_name):
        config = {}
        parsed_url = urlparse(self._servers[server_name])
        config['host'] = parsed_url.hostname
        config['database'] = database_name
        if parsed_url.port:
            config['port'] = parsed_url.port
        if parsed_url.username:
            config['user'] = parsed_url.username
        if parsed_url.password:
            config['password'] = parsed_url.password

        return Database(self._client_factory(config))
