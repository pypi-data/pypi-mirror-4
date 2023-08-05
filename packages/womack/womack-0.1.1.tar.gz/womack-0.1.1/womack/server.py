import os
import sys
from optparse import OptionParser
try:
    from bottle import Bottle, debug, request, static_file
    from socketio import server, socketio_manage
except ImportError, e:
    raise ImportError("Server requirement not found: %s. "
                      "Try pip install -r requirements-server.txt" % e)
from . import namespace
from .config import config

HERE = os.path.abspath(os.path.dirname(__file__))
STATIC = os.path.join(HERE, 'static')


app = Bottle()


@app.route('/socket.io/<arg:path>')
def socketio(*arg, **kw):
    socketio_manage(request.environ, namespace.REGISTRY, request=request)
    return "out"


@app.route('/<filename:path>')
def static(filename):
    return static_file(filename, root=STATIC)


def parse_argv(argv=None):
    """Parse command line arguments"""
    if argv is None:
        argv = sys.argv[:]
    parser = OptionParser()
    parser.add_option('-H', '--host', dest='host', default='0.0.0.0')
    parser.add_option('-p', '--port', dest='port', default=8111, type=int)
    parser.add_option('--redis-host', dest='redis_host', default='localhost')
    parser.add_option('--redis-port', dest='redis_port', default=6379, type=int)
    parser.add_option('--debug', action='store_true', default=False)
    opts, args = parser.parse_args()
    config.configure(opts.__dict__)
    if opts.debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)
        debug(True)
    return opts


def main(argv=None):
    """Parse command-line arguments and start the server"""
    opts = parse_argv(argv)
    if opts.debug:
        from dozer import Dozer
        app_ = Dozer(app)
    else:
        app_ = app
    server.SocketIOServer(
        (config.host, config.port), app_, policy_server=False).serve_forever()


if __name__ == '__main__':
    main()
