# -*- coding: utf-8 -*-
"""The tgapp-photos package"""

def plugme(app_config, options):
    app_config['_pluggable_photos_config'] = options
    return dict(appid='photos', global_helpers=False)