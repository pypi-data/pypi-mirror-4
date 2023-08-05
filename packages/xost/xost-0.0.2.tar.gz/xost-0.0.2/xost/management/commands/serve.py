# -*- coding: utf-8 -*-

import os
from optparse import make_option
from django.core.management import BaseCommand
from xost.config import EmbdedConfig
from xost.server import Server


class Command(BaseCommand):
    help = '%s embded server' % Server.version
    can_import_settings = True

    option_list = BaseCommand.option_list + (
        make_option('-d', '--daemonize',
            action='store_true',
            dest='daemonize',
            help='launch as daemon (whether to detach from terminal)'
        ),
        make_option('--pid',
            action='store',
            dest='pidfile',
            help='write the spawned process-id to this file. '
        ),
        make_option('-a', '--address',
            action='store',
            dest='address',
            help='string configuration listen addresses'
        ),
        make_option('-p', '--port',
            action='store',
            dest='port',
            type='int',
            help='a port number on which to listen'
        ),
        make_option('--min_threads',
            action='store',
            dest='min_threads',
            type='int',
            help='minimum number of threads in the pool'
        ),
        make_option('--max_threads',
            action='store',
            dest='max_threads',
            type='int',
            help='maximum number of threads in the pool'
        ),
        make_option('--root',
            action='store',
            dest='root',
            help='path to working (root) folder'
        ),
        make_option('--static_root',
            action='store',
            dest='static_root',
            help='path to static file folder'
        ),
        make_option('--media_root',
            action='store',
            dest='static_root',
            help='path to media file folder'
        ),
        make_option('--log_path',
            action='store',
            dest='log_path',
            help='path to log folder'
        ),
        make_option('--no_static',
            action='store_false',
            dest='collect_static',
            help='do not collect static files to  static root folder before launch'
        ),
        )

    def handle(self, *args, **options):
        from django.conf import settings

        conf = EmbdedConfig(settings)
        settings.STATIC_ROOT = conf.static_root
        settings.MEDIA_ROOT = conf.media_root

        if not conf.debug:
            conf.debug = settings.DEBUG

        for key, val in options.iteritems():
            if hasattr(conf, key) and val is not None:
                setattr(conf, key, val)
            pass

        #if not conf.log_path:
        #    log_name = os.environ['DJANGO_SETTINGS_MODULE']
        #    log_name = log_name[:log_name.rfind('.')] + '.access.log'
        #    conf.log_path = os.path.join(conf.root, 'log', log_name)


        server = Server(conf)

        if options['daemonize']:
            from django.utils.daemonize import become_daemon
            become_daemon(our_home_dir=conf.root)

        if options["pidfile"]:
            fp = open(options["pidfile"], "w")
            fp.write("%d\n" % os.getpid())
            fp.close()

        server.run()

    pass
