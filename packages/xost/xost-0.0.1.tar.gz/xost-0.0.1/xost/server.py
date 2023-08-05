# -*- coding: utf-8 -*-

import os
from twisted.python import threadpool
from twisted.web import server, resource, wsgi, static
from twisted.internet import reactor
from twisted.internet.endpoints import serverFromString
from django.core.handlers.wsgi import WSGIHandler
from django.core.management import call_command
from xost import __version__

server.version = 'Xost/%s' % __import__('xost').__version__

class WSGI(resource.Resource):
    def __init__(self, min_threads=5, max_threads=20):
        resource.Resource.__init__(self)
        self.pool = threadpool.ThreadPool(min_threads, max_threads)
        reactor.addSystemEventTrigger('after', 'shutdown', self.pool.stop)
        self.wsgi_resource = wsgi.WSGIResource(reactor, self.pool, WSGIHandler())
        self.pool.start()

    def getChild(self, path, request):
        path0 = request.prepath.pop(0)
        request.postpath.insert(0, path0)
        return self.wsgi_resource

    pass


class File(static.File):
    def __init__(self, path, defaultType="text/html", ignoredExts=(), registry=None, allowExt=0, dirList=False):
        self.dirList = dirList
        super(File, self).__init__(path, defaultType, ignoredExts, registry, allowExt)

    def directoryListing(self):
        if not self.dirList:
            return resource.ForbiddenResource()
        return super(File, self).directoryListing()

    pass


class Site(server.Site):
    def __init__(self, config):
        self.config = config
        self.root = WSGI(config.min_threads, config.max_threads)
        self.wsgi_pool = self.root.pool
        self.root.putChild('static', File(config.static_root))
        self.root.putChild('media', File(config.media_root))
        server.Site.__init__(self, self.root, config.log_path)

    pass


class Server(object):
    version = server.version

    def __init__(self, config):
        self.config = config

    def run(self):
        conf = self.config
        if conf.debug:
            print server.version
            print
            print 'Resources:'
            print '\troot:', conf.root
            print '\tstatic:', conf.static_root
            print '\tmedia:', conf.media_root
            print '\tlog:', conf.log_path
        if conf.log_path and not os.path.exists(conf.log_path):
            if not os.path.exists(os.path.dirname(conf.log_path)):
                os.makedirs(os.path.dirname(conf.log_path))
            f = open(conf.log_path, 'w')
            f.close()
        if conf.collect_static:
            call_command('collectstatic', interactive=False)
        site = Site(conf)
        try:
            if conf.address:
                srv = serverFromString(reactor, conf.address)
                srv.listen(site)
            else:
                reactor.listenTCP(conf.port, site)
            reactor.run()
        except Exception, ex:
            if site.root:
                site.wsgi_pool.stop()
            raise ex
        pass

    pass
