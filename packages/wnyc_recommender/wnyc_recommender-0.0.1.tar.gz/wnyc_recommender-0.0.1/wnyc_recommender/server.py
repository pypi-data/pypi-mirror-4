import fetcher 
import gevent
import gevent.monkey 
from engine import Engine
from fetcher import Fetcher
import BaseHTTPServer
import gflags
import json

FLAGS = gflags.FLAGS
gflags.DEFINE_string('host', '0.0.0.0', 'Addr to bind to')
gflags.DEFINE_integer('port', 8000, 'port to bind to')

gevent.monkey.patch_all()


class Server(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            ident = int(self.path[1:])
        except ValueError:
            return self.send_response(404, 'This is not the file you are looking for')
        self.send_response(200)
        self.send_header("Content-type", "text/json")
        self.end_headers()

        self.wfile.write(json.dumps(engine.recommend(ident)))


def run():
    global engine 
    engine = Engine()
    gevent.spawn(Fetcher.loadall, **dict(notify=engine.intake))
    httpd = BaseHTTPServer.HTTPServer((FLAGS.host, FLAGS.port), Server)
    try:
        while True:
            httpd.handle_request()
    except KeyboardInterrupt:
        pass


    
    
