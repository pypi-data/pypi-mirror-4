import SimpleXMLRPCServer

class Server(object):
    def __init__(self, host, port=4200):
        port = int(port)
        self.host = host
        self.server = SimpleXMLRPCServer.SimpleXMLRPCServer(('', port), allow_none=True)
        self.server.register_instance(self)

    def serve(self):
        self.server.serve_forever()

    def _dispatch(self, method, params):
        value = getattr(self.host, method)
        try:
            return value(*params)
        except TypeError:
            return value
