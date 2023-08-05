import logging
import argparse
import time, signal

import zmq
from zmq.eventloop import zmqstream
from zmq.eventloop import ioloop

ioloop.install()

from tornado import web
from sockjs.tornado import SockJSRouter, SockJSConnection

from tornado.httpserver import HTTPServer


log = logging.getLogger("sockjsproxy")


class BackendConnection(object):
    def __init__(self, io_loop, in_socket, out_socket):
        self.zmq_in = zmqstream.ZMQStream(in_socket, io_loop=io_loop)
        self.zmq_out = zmqstream.ZMQStream(out_socket, io_loop=io_loop)
        self.zmq_out.on_recv(self.on_recv)

    def set_frontend_connection(self, frontend):
        self.frontend = frontend

    def on_recv(self, data):
        try:
            command, session_id, message = data
        except ValueError:
            log.warn("Recieved invalid data: %s. Expected [command|session_id|data] multipart message.")
            return

        log.debug('Got %s from ZMQ for %s: %s', command, session_id, data)
        if command == 'message':
            self.frontend.send(session_id, message)
        elif command == 'disconnect':
            # TODO: Drop the connection
            pass
        else:
            log.warn("Invalid command %s", command)

    def send_message(self, session_id, message):
        log.debug('Sending message over ZMQ from %s: "%s"', session_id, message)
        self.zmq_in.send_multipart(['message', str(session_id), message.encode('utf-8')])

    def send_session_connect(self, session_id):
        self.zmq_in.send_multipart(['connect', str(session_id), ''])

    def send_session_disconnect(self, session_id):
        self.zmq_in.send_multipart(['disconnect', str(session_id), ''])


class FrontendTransport(SockJSConnection):
    """
    The actual sock.js connection. Since the library creates one instance
    of this class for every connection we use the python id() of the instance
    as session_id, and all session_ids should be unicode so we can find
    them easily in dicts.
    """
    frontend = None

    @classmethod
    def initialize(cls, frontend):
        cls.frontend = frontend

    def on_open(self, request):
        self.frontend.add_session(unicode(id(self)), self)

    def on_message(self, msg):
        self.frontend.message_from_client(unicode(id(self)), msg)

    def on_close(self):
        self.frontend.remove_session(unicode(id(self)))


class FrontendConnection(object):
    """
    Connection, responsible for handling messages from SockJS.
    """

    def __init__(self):
        self.sessions = {}

    def set_backend_connection(self, backend):
        self.backend = backend

    def add_session(self, session_id, connection):
        self.sessions[session_id] = connection
        self.backend.send_session_connect(session_id)
        log.debug('Session %s established', session_id)

    def remove_session(self, session_id):
        if session_id not in self.sessions:
            log.warn('Session %s missing when removing', session_id)
            return

        del self.sessions[session_id]

        self.backend.send_session_disconnect(session_id)
        log.debug('Session %s removed', session_id)

    def message_from_client(self, session_id, raw_message):
        log.debug('Receiving raw message from client %s: "%s"', session_id, raw_message)
        if raw_message == 'echo':
            self.sessions[session_id].send('echo')
            log.debug('Sending "echo" back to %s', session_id)
            return

        self.backend.send_message(session_id, raw_message)

    def send(self, session_id, message):
        connection = self.sessions.get(session_id)
        if not connection:
            log.warn('Could not send message to session %s: "%s". '
                     'Connection not found.', session_id, message)
            return

        connection.send(message)


class SockJSProxy(object):
    def collect_args(self):
        parser = argparse.ArgumentParser(description="Proxy messages between sock.js and a 0MQ socket")
        parser.add_argument('--address', '-a', type=str,
                            help="The 0MQ address to listen to. Defaults to * (meaning - everything)",
                            default='*')

        parser.add_argument('--in-port', '-i', type=int,
                            help="The port to listen for incoming 0MQ connections. Defaults to 9241",
                            default=9241)
        parser.add_argument('--out-port', '-o', type=int,
                            help="The port to listen for outgoing 0MQ connections. Defaults to 9242",
                            default=9242)

        parser.add_argument('--http-port', '-p', type=int,
                            help="The port to listen for http (sock.js) connections. Defaults to 8080",
                            default=8080)

        parser.add_argument('--static-path', '-s', type=str,
                            help="The path to a local static directory to be served under --static-url")
        parser.add_argument('--static-url', '-u', type=str,
                            help="The url where the files in --static-path will be served")

        parser.add_argument('--samples', type=str,
                            help='Serve samples under SAMPLES path')
        parser.add_argument('--verbose', action='store_true', default=False,
                            help='Make the server output more information - useful for debugging')

        args = parser.parse_args()

        if bool(args.static_path) != bool(args.static_url):
            parser.error("You should specify both --static-path and --static-url to have static files served.")

        return args

    def init_logging(self, verbose):
        log.setLevel(logging.DEBUG if verbose else logging.INFO)

    def main(self):
        args = self.collect_args()
        self.init_logging(args.verbose)

        in_address = "tcp://{}:{}".format(args.address, args.in_port)
        out_address = "tcp://{}:{}".format(args.address, args.out_port)

        log.info("Pushing incoming messages to:   %s", in_address)
        log.info("Pulling outgoing messages from: %s", out_address)

        ctx = zmq.Context()
        in_socket = ctx.socket(zmq.PUB)
        in_socket.bind(in_address)
        out_socket = ctx.socket(zmq.SUB)
        out_socket.bind(out_address)
        out_socket.setsockopt(zmq.SUBSCRIBE, '')

        io_loop = ioloop.IOLoop.instance() # ZMQ loop

        frontend = FrontendConnection()
        backend = BackendConnection(io_loop, in_socket, out_socket)

        FrontendTransport.initialize(frontend)
        frontend.set_backend_connection(backend)
        backend.set_frontend_connection(frontend)

        sockjs_router = SockJSRouter(FrontendTransport, io_loop=io_loop)

        routes = sockjs_router.urls

        if args.samples:
            sample_url = '/' + args.samples.strip('/')
            import os.path as p
            sample_path = p.join(p.abspath(p.dirname(__file__)), 'samples')
            print sample_path
            log.info("Serving samples content at %s", sample_url)
            routes += [(r"%s/?(.*)" % sample_url, web.StaticFileHandler,
                        {"path": sample_path, "default_filename": "index.html"}),
                       (r"%s()" % sample_url, web.StaticFileHandler,
                        {"path": sample_path, "default_filename": "index.html"})]

        if args.static_path and args.static_url:
            static_url = '/' + args.static_url.strip('/')
            log.info("Serving static directory %s at %s", args.static_path, static_url)
            routes += [(r"%s/?(.*)" % static_url, web.StaticFileHandler,
                        {"path": args.static_path, "default_filename": "index.html"}),
                       (r"%s()" % static_url, web.StaticFileHandler,
                        {"path": args.static_path, "default_filename": "index.html"})]

        web_app = web.Application(routes, debug=False)

        web_server = HTTPServer(web_app)
        web_server.listen(args.http_port)

        def term(*_ignore):
            log.info("SockjsProxy shutting down...")
            web_server.stop()
            io_loop.add_timeout(time.time() + 0.3, io_loop.stop)
            io_loop.start() # Let the IO loop finish its work

        signal.signal(signal.SIGTERM, term)

        try:
            log.info('SockjsProxy serving on %s', args.http_port)
            io_loop.start()
        except KeyboardInterrupt:
            term()

