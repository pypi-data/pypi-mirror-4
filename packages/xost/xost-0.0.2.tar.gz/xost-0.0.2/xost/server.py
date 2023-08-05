# -*- coding: utf-8 -*-

import os
from importlib import import_module
from twisted.python import threadpool
from twisted.web import server, resource
from twisted.internet import reactor
from twisted.internet.endpoints import serverFromString
from django.core.handlers.wsgi import WSGIHandler
from django.core.management import call_command
from xost.utils import url_to_list
from xost.resources import Resource, File, WSGIResource


server.version = 'Xost/%s' % __import__('xost').__version__


class WSGI(Resource):
    def __init__(self, min_threads=5, max_threads=20):
        resource.Resource.__init__(self)
        self.pool = threadpool.ThreadPool(min_threads, max_threads)
        reactor.addSystemEventTrigger('after', 'shutdown', self.pool.stop)
        self.wsgi_resource = WSGIResource(reactor, self.pool, WSGIHandler())
        self.pool.start()

    def getChild(self, path, request):
        path0 = request.prepath.pop(0)
        request.postpath.insert(0, path0)
        return self.wsgi_resource

    pass


class Site(server.Site):
    def __init__(self, config):
        self.config = config
        self.root = WSGI(config.min_threads, config.max_threads)
        self.wsgi_pool = self.root.pool
        try:
            self.root.putChildIntoUrl(config.static_url, File(config.static_root))
            self.root.putChildIntoUrl(config.media_url, File(config.media_root))
            self.initStorages()
            server.Site.__init__(self, self.root, config.log_path)
        except Exception, ex:
            self.wsgi_pool.stop()
            raise ex
        pass

    def initStorages(self):
        for storage in self.config.storages:
            if not isinstance(storage, (list, tuple)) or len(storage) < 2 or len(storage) > 3:
                raise ValueError('Incorrect definition of storage: %s' % repr(storage))
            storage = list(storage)
            prefix_length = len(url_to_list(storage[0])) + 1
            if len(storage) == 2:
                storage.append({})
            url = self.config.media_url + storage[0]
            path = os.path.normpath(os.path.join(self.config.media_root, storage[0]))
            res = storage[1]
            if isinstance(res, str):
                mdl = import_module(res[:res.rfind('.')])
                res = getattr(mdl, res[res.rfind('.') + 1:])

                res = res(path, **storage[2])
            res._prefixLength = prefix_length
            self.root.putChildIntoUrl(url, res)
        pass

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
