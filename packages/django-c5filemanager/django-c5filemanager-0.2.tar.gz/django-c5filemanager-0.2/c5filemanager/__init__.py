# -*- coding: utf-8 -*-
"""c5filemanager package, Django connector for Core Five Filemanager.

THIS SOFTWARE IS UNDER BSD LICENSE.
Copyright (c) 2010-2012 Daniele Tricoli <eriol@mornie.org>

Read LICENSE for more informations.
"""
VERSION = (0, 2)

def get_version():
    """Returns project version in a human readable form."""
    version = '.'.join(str(v) for v in VERSION[:3])
    sub = ''.join(str(v) for v in VERSION[3:])
    return version + sub
