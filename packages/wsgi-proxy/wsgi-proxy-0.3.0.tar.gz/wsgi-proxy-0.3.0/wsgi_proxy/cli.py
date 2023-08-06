""":mod:`wsgi_proxy.cli` --- :program:`wsgi-proxy` command
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. program:: wsgi-proxy

.. option:: -h, --help

   Print help message.

.. option:: -p <port>, --port <port>

   The port number to listen.  Default is 8080.

.. option:: -H <host>, --host <host>

   The hostname to listen.  Default is ``127.0.0.1``.

.. option:: --server <server>

   The WSGI server implementation to use.  Default is ``waitress``.

.. option:: -v, --verbose

   Print debug logs as well.  It internally sets :mod:`logging` level
   to :const:`~logging.DEBUG`.

.. option:: -q, --quiet

   Operate quitely.  It internally sets :mod:`logging` level
   to :const:`~logging.ERROR`.

"""
import functools
import logging
import optparse
import sys
import wsgiref.simple_server

from . import app


try:
    import waitress
    import waitress.channel
    import waitress.server
    import waitress.task
except KeyError:
    DEFAULT_SERVER = 'wsgiref'
else:
    class WaitressWSGIServer(waitress.server.WSGIServer):
        class channel_class(waitress.channel.HTTPChannel):
            class task_class(waitress.task.WSGITask):
                def get_environment(self):
                    env = waitress.task.WSGITask.get_environment(self)
                    req = self.request
                    if req.proxy_scheme and req.proxy_netloc:
                        env['PATH_INFO'] = '{0}://{1}{2}'.format(
                            req.proxy_scheme,
                            req.proxy_netloc,
                            env['PATH_INFO']
                        )
                    return env
    run_waitress = functools.partial(waitress.serve, _server=WaitressWSGIServer)
    DEFAULT_SERVER = 'waitress'


parser = optparse.OptionParser()
parser.add_option('-p', '--port', type='int', default=8080,
                  help='Port number [default: %default]')
parser.add_option('-H', '--host', default='127.0.0.1',
                  help='Host [default: %default]')
parser.add_option('--server', default=DEFAULT_SERVER,
                  help='Server implementation [default: %default]')
parser.add_option('-v', '--verbose', action='store_const',
                  dest='log_level', const=logging.DEBUG,
                  help='Print debug logs as well')
parser.add_option('-q', '--quiet', action='store_const',
                  dest='log_level', const=logging.ERROR, default=logging.INFO,
                  help='Operate quietly')


def run_wsgiref(app, host, port):
    server = wsgiref.simple_server.make_server(host, port, app)
    logger = logging.getLogger(__name__ + '.run_wsgiref')
    logger.info('Running proxy at http://%s:%s', host, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        raise SystemExit


try:
    from cherrypy.wsgiserver import CherryPyWSGIServer
except ImportError:
    pass
else:
    def run_cherrypy(app, host, port):
        server = CherryPyWSGIServer((host, port), app, server_name='wsgi_proxy')
        server.start()
        try:
            while 1:
                pass
        except KeyboardInterrupt:
            server.stop()
            raise SystemExit


def main():
    options, args = parser.parse_args()
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(options.log_level)
    servers = dict((k[4:], v)
                   for k, v in globals().items()
                   if k.startswith('run_'))
    try:
        serve = servers[options.server]
    except KeyError:
        parser.error(options.server +
                     ' is not a supported server implementation')
    serve(app=app, host=options.host, port=options.port)


if __name__ == '__main__':
    main()
