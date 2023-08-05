# -*- coding: utf-8 -*-

import datetime
from importlib import import_module
from twisted.web import resource, static, wsgi
from twisted.web.util import redirectTo
from twisted.internet.address import UNIXAddress
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME, BACKEND_SESSION_KEY, SESSION_KEY, load_backend
from django.contrib.auth.models import AnonymousUser
from xost.utils import url_to_list


class _WSGIResponse(wsgi._WSGIResponse):
    def __init__(self, reactor, threadpool, application, request):
        if isinstance(request.getHost(), UNIXAddress):
            setattr(request.getHost(), 'port', 80)
        super(_WSGIResponse, self).__init__(reactor, threadpool, application, request)

    pass


class WSGIResource(wsgi.WSGIResource):
    def render(self, request):
        response = _WSGIResponse(
            self._reactor, self._threadpool, self._application, request)
        response.start()
        return wsgi.NOT_DONE_YET

    pass


class UrlMixin:
    def putChildIntoUrl(self, url, child):
        path = url_to_list(url)
        _child = self
        for i in range(len(path)):
            if not _child.children.has_key(path[i]) or i == len(path) - 1:
                if i < len(path) - 1:
                    _child = _child.putChild(path[i], Resource())
                else:
                    _child = _child.putChild(path[i], child)
                pass
            else:
                _child = _child.children[path[i]]
            pass
        pass

    pass


class Resource(resource.Resource, UrlMixin):
    def getChild(self, path, request):
        return resource.ForbiddenResource()

    def putChild(self, path, child):
        resource.Resource.putChild(self, path, child)
        return self.children[path]

    pass


class File(static.File):
    def __init__(self, path, defaultType="text/html", ignoredExts=(), registry=None, allowExt=0, dirList=False):
        super(File, self).__init__(path, defaultType, ignoredExts, registry, allowExt)
        self.dirList = dirList

    def directoryListing(self):
        if not self.dirList:
            return resource.ForbiddenResource()
        return super(File, self).directoryListing()


    def createSimilarFile(self, path):
        f = super(File, self).createSimilarFile(path)
        f.dirList = self.dirList
        return f

    pass


class AuthFile(File):
    _session_engine = import_module(settings.SESSION_ENGINE)
    _prefixLength = -1

    def __init__(self, path, defaultType="text/html", ignoredExts=(), registry=None, allowExt=0, dirList=False,
                 noCache=True):
        self.dirList = dirList
        self.noCache = noCache
        super(AuthFile, self).__init__(path, defaultType, ignoredExts, registry, allowExt)

    def getUser(self, request):
        session_key = request.getCookie(settings.SESSION_COOKIE_NAME)
        session = self._session_engine.SessionStore(session_key)
        try:
            user_id = session[SESSION_KEY]
            backend = load_backend(session[BACKEND_SESSION_KEY])
            user = backend.get_user(user_id) or AnonymousUser()
        except KeyError:
            user = AnonymousUser()
        return user

    def isUserAuth(self, user, request):
        if user.is_authenticated():
            return True
        return False

    def render(self, request):
        if len(request.prepath) <= self._prefixLength:
            return resource.NoResource().render(request)
        else:
            user = self.getUser(request)
            if user.is_anonymous():
                return redirectTo('%s?%s=%s' % (settings.LOGIN_URL, REDIRECT_FIELD_NAME, request.path), request)
            elif not self.isUserAuth(user, request):
                return resource.NoResource().render(request)

            pass
        if self.noCache:
            request.setHeader('Cache-Control', 'no-cache, must-revalidate, max-age=0')
            request.setHeader('Pragma', 'no-cache')
            request.setHeader('Expires', datetime.datetime.strftime(
                datetime.datetime.utcnow() - datetime.timedelta(seconds=1), '%a, %d %b %Y %H:%M:%S GMT'
            ))
        return super(AuthFile, self).render(request)

    def createSimilarFile(self, path):
        f = super(AuthFile, self).createSimilarFile(path)
        f.noCache = self.noCache
        f._prefixLength = self._prefixLength = self._prefixLength
        return f

    pass


class UserFile(AuthFile):
    def isUserAuth(self, user, request):
        if user.is_superuser or user.username == request.prepath[self._prefixLength]:
            return True
        return False

    pass



