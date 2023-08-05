.. _available_settings:

Available Settings
==================

Main ROOT/URL Settings
----------------------

Absolute path of the directory that holds your media files::

    MEDIA_ROOT = getattr(settings, 'C5FILEMANAGER_MEDIA_ROOT', settings.MEDIA_ROOT)

URL that handles the media served from ``MEDIA_ROOT``::

    MEDIA_URL = getattr(settings, 'C5FILEMANAGER_MEDIA_URL', settings.MEDIA_URL)

File manager Media Path
-----------------------

Path of the django-c5filemanager media files::

    C5FILEMANAGER_MEDIA = getattr(settings, 'C5FILEMANAGER_MEDIA', 'filemanager')

.. important::
    Specified path must be relative to ``STATIC_ROOT``.

File manager Upload Directory
-----------------------------

Path of the django-c5filemanager upload directory::

    UPLOAD_DIRECTORY = getattr(settings, 'C5FILEMANAGER_UPLOAD_DIRECTORY', 'upload')

.. important::
    Specified path will be *always* relative to ``MEDIA_ROOT``.
