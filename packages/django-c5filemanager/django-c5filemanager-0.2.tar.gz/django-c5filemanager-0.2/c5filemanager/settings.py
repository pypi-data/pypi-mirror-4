# -*- coding: utf-8 -*-
"""c5filemanager.settings module, custom settings for django-c5filemanager.

THIS SOFTWARE IS UNDER BSD LICENSE.
Copyright (c) 2010-2012 Daniele Tricoli <eriol@mornie.org>

Read LICENSE for more informations.
"""
import posixpath

from django.conf import settings

# Main MEDIA settings
MEDIA_ROOT = getattr(settings, 'C5FILEMANAGER_MEDIA_ROOT', settings.MEDIA_ROOT)
MEDIA_URL = getattr(settings, 'C5FILEMANAGER_MEDIA_URL', settings.MEDIA_URL)

# django-c5filemanager media path. Must be relative to STATIC_ROOT.
C5FILEMANAGER_MEDIA = getattr(settings, 'C5FILEMANAGER_MEDIA', 'filemanager')

# django-c5filemanager upload directory. Must be relative to MEDIA_ROOT.
UPLOAD_DIRECTORY = getattr(settings,
                           'C5FILEMANAGER_UPLOAD_DIRECTORY',
                           'upload')

# django-c5filemanager upload directory relative to MEDIA_URL.
UPLOAD_DIRECTORY_URL = posixpath.join(MEDIA_URL, UPLOAD_DIRECTORY)
