# -*- coding: utf-8 -*-
"""The tgapp-smallpress package"""
import tg, os, logging
from tgext.pluggable import plugged, plug

log = logging.getLogger('tgapp-smallpress')

def plugme(app_config, options):
    tg.config['_smallpress'] = options

    if 'tgext.tagging' not in plugged():
        plug(app_config, 'tgext.tagging')

    def init_whoosh(app):
        try:
            from whoosh.index import create_in
            log.info('Enabling Whoosh Support')
            whoosh_enabled = True
        except ImportError:
            log.info('Whoosh Not Found, disabled')
            whoosh_enabled = False

        if whoosh_enabled:
            from smallpress.model.models import WHOOSH_SCHEMA
            index_path = tg.config.get('smallpress_whoosh_index', '/tmp/smallpress_whoosh')
            if not os.path.exists(index_path):
                os.mkdir(index_path)
                ix = create_in(index_path, WHOOSH_SCHEMA)

        return app

    app_config.register_hook('before_config', init_whoosh)
    return dict(appid='smallpress', global_helpers=False)
