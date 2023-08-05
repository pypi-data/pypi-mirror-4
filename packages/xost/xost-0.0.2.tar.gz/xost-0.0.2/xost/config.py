# -*- coding: utf-8 -*-


from django.utils.importlib import import_module

import os

class Config:
    address = None
    port = 8080
    min_threads = 5
    max_threads = 20
    root = None
    static_root = None
    static_url = None
    media_root = None
    media_url = None
    log_path = None
    collect_static = True
    debug = False
    storages = []

    def __init__(self):
        self.root = self.root or os.getcwd()
        self.static_root = self.static_root or os.path.join(self.root, 'static')
        self.static_url = self.static_url or '/static/'
        self.media_root = self.media_root or os.path.join(self.root, 'media')
        self.media_url = self.media_url or '/media/'

        if self.address:
            self.address = self.address.strip()
            if self.address.find(':lockfile=') == -1:
                self.address += ':lockfile=0'
            if self.address.find(':mode=') == -1:
                self.address += ':mode=0660'
            pass
        pass

    pass


class EmbdedConfig(Config):
    def __init__(self, settings=None):
        settings = settings or import_module(os.environ['DJANGO_SETTINGS_MODULE'])
        if hasattr(settings, 'XOST'):
            for key, val in getattr(settings, 'XOST').iteritems():
                setattr(self, key, val)
            pass
        if not self.static_url and len(settings.STATIC_URL.strip()) > 0:
            self.static_url = settings.STATIC_URL.strip()
        if not self.media_url and len(settings.MEDIA_URL.strip()) > 0:
            self.media_url = settings.MEDIA_URL.strip()
        Config.__init__(self)

    pass

