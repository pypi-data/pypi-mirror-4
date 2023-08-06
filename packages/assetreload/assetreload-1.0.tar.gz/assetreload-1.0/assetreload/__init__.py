#!/usr/bin/env python

import tornado.ioloop
import tornado.web
import tornado.websocket
import watchdog.observers
import watchdog.events
import logging
import os
import sys
import shutil
import mimetypes
import pkg_resources

from tornado.options import define, options

define('port', default=8888, help='run on the given port', type=int)
define('path', default=os.getcwd(),
       help='watch files in the given directory', type=str)


connections = set()
watch_path = None

class AssetReloadWebSocket(tornado.websocket.WebSocketHandler):
    def open(self):
        self.connected_host = self.get_argument('host')
        self.watched_files = self.request.arguments['file']
        connections.add(self)
        print '%s connected' % self.connected_host

    def on_message(self, message):
        pass

    def on_close(self):
        connections.remove(self)
        print '%s disconnected' % self.connected_host


class FileModifiedHandler(watchdog.events.FileSystemEventHandler):
    def on_modified(self, info):
        path = os.path.relpath(info.src_path, watch_path)
        mimetype = mimetypes.guess_type(path)[0]

        for connected in connections:
            try:
                if path in connected.watched_files:
                    connected.write_message(dict(path=path,
                                                 mimetype=mimetype))
            except:
                logging.error('Error sending message', exc_info=True)


def generate_javascript(dir):
    shutil.copy(pkg_resources.resource_filename(__name__, 'assetreload.js'),
					      dir)
    print 'Generated script to %s' % os.path.join(dir, 'assetreload.js')


def main():
    global watch_path

    tornado.options.parse_command_line()
    watch_path = os.path.expanduser(options.path)

    if 'genscript' in sys.argv:
        generate_javascript(watch_path)
        sys.exit()

    observer = watchdog.observers.Observer()
    application = tornado.web.Application([(r'/assetreload',
                                            AssetReloadWebSocket)])

    print ('Server started at http://localhost:%s/assetreload, '
           'watching %s') % (options.port, options.path)

    application.listen(options.port)
    observer.schedule(FileModifiedHandler(), watch_path, recursive=True)

    try:
        observer.start()
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
