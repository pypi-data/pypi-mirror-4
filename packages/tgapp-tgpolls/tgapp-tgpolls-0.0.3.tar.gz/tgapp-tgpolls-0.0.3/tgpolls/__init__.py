# -*- coding: utf-8 -*-
"""The tgapp-tgpolls package"""

import tg

def plugme(app_config, options):
    tg.config['_tgext_tgpolls'] = options
    return dict(appid='tgpolls', global_helpers=False)