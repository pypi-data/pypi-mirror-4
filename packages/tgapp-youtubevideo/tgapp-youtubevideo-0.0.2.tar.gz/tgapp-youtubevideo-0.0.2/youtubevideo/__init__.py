# -*- coding: utf-8 -*-
"""The youtubevideo package"""

def plugme(app_config, options):
    if 'user' not in options:
        options['user'] = 'PythonItalia'
    if 'refresh' not in options:
        options['refresh'] = 3600
    app_config['_pluggable_youtubevideo_config'] = options
    return dict(appid='youtubevideo', global_helpers=False)