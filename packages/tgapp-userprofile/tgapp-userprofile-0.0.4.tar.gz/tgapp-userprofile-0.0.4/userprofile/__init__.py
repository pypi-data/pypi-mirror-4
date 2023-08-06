# -*- coding: utf-8 -*-
"""The userprofile package"""

def plugme(app_config, options):
    app_config['_pluggable_userprofile_config'] = options
    return dict(appid='userprofile', global_helpers=False)
