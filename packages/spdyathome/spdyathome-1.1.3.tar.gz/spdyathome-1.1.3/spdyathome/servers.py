"""
Start the basic thor servers for each case of connection.
Use the standard request responders in BaseServer.
"""
import yaml
import logging
import argparse
from thor.loop import run
from thor import HttpServer
from thor import SpdyServer
from serverbase import BaseServer
from multiprocessing import Process
from thor.events import on
import urilib
import util
import os


def get_args():
    parser = argparse.ArgumentParser(
            description='Run SPDY and HTTP servers to act as endpoint of test.',
            epilog='This can be run directly or using `scripts/run-servers`.')
    parser.add_argument('-c', '-config', type=str, required=False,
            dest='conf_file', action='store', help='YAML configuration file.')
    return parser.parse_args()


def http_main(conf):
    print 'Loading configuration into http base server!'
    base = BaseServer(conf)
    print 'creating HTTP server on port %d' % (conf['http_port'],)

    def http_handler(x):
        @on(x, 'request_start')
        def go(*args):
            print 'HTTP: start %s' % (str(args[1]),)
            base.paths.get(util.make_ident(x.method, x.uri), base.fourohfour)(x)

        @on(x, 'request_body')
        def body(chunk):
            #print 'body: %s' % chunk
            pass

        @on(x, 'request_done')
        def done(trailers):
            #print 'done: %s' % str(trailers)
            pass

    http_serve = HttpServer(host='', port=conf['http_port'])
    http_serve.on('exchange', http_handler)


def spdy_main(conf):
    print 'Loading configuration into spdy base server!'
    base = BaseServer(conf)
    print 'creating SPDY server on port %d' % (conf['spdy_port'],)

    def spdy_handler(x):
        @on(x, 'request_start')
        def go(*args):
            path = urilib.URI(x.uri).path  # Take into account SPDY's uri
            print 'SPDY: start %s' % (path,)
            base.paths.get(util.make_ident(x.method, path), base.fourohfour)(x)

        @on(x, 'request_body')
        def body(chunk):
            #print 'body: %s' % chunk
            pass

        @on(x, 'request_done')
        def done(trailers):
            #print 'done: %s' % str(trailers)
            pass

    spdy_serve = SpdyServer('', conf['spdy_port'])
    spdy_serve.on('exchange', spdy_handler)


def capture_main(conf):
    print 'creating capture server on port %d' % (conf['capture_port'],)

    def capture_handler(x):
        up = {'inp': '', 'final': {}}

        @on(x, 'request_start')
        def go(*args):
            print 'capture: start %s' % (str(args[1]),)

        @on(x, 'request_body')
        def body(chunk):
            up['inp'] += chunk

        @on(x, 'request_done')
        def done(trailers):
            with open(os.path.join(conf['outdir'], conf['outfile']), 'a') as f:
                f.write(up['inp'])
                f.write('\n')
                f.close()
            print 'finished capture'
            x.response_start(200, 'OK', [])
            x.response_done([])

    capture_serve = HttpServer(host='', port=conf['capture_port'])
    capture_serve.on('exchange', capture_handler)

if __name__ == '__main__':
    args = get_args()
    #conf = yaml.load(file(args.conf_file, 'r'))
    dirpath = os.path.dirname(__file__)
    conf = yaml.load(file(os.path.join(dirpath, 'conf.yaml'), 'r'))

    try:
        os.mkdir(conf['outdir'])
    except OSError:
        pass

    capture_main(conf)
    spdy_main(conf)
    http_main(conf)
    run()
