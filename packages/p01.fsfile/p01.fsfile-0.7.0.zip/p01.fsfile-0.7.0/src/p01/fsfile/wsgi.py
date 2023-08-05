###############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""
$Id:$
"""

from zope.app.appsetup.product import _configs as productConfigs


def configureFSStorage(local_conf, confKey='storage'):
    storage = local_conf.get(confKey)
    if storage is None:
        raise ValueError(
            "Missing p01.fsfile '%s' configuration in paste *.ini file" % confKey)
    productConfigs.update({'p01.fsfile': {confKey: storage}})
