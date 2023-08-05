Getting Started
===============

Installing django-c5filemanager
-------------------------------

``django-c5filemanager`` requires `Django <http://www.djangoproject.com>`_
version 1.1 or superior,
`simplejson <http://undefined.org/python/#simplejson>`_ version 2.1.0 or
superior and `PIL <http://www.pythonware.com/products/pil/>`_.

You can choose to install ``django-c5filemanager`` automatically or manually.

Automatic installation
~~~~~~~~~~~~~~~~~~~~~~

Simply install ``django-c5filemanager`` using ``pip``::

    $ pip install django-c5filemanager

Alternatively you can directly install from a packaged version or from the
mercurial repository using ``pip``.

For example, if you want to install version 0.2 from the mercurial repository
you have to do::

    $ pip install -e http://hg.mornie.org/django/c5filemanager/@0.2#egg=django-c5filemanager

Or from the packaged version::

    $ pip install http//downloads.mornie.org/django-c5filemanager/django-c5filemanager-0.2.tar.gz

Manual installation
~~~~~~~~~~~~~~~~~~~

You can download packaged version from http://downloads.mornie.org/django-c5filemanager
and and use Python's ``distutils`` to install.

Required settings
-----------------

Once installed, you can start using ``django-c5filemanager`` in your Django
project adding ``c5filemanager`` to the ``INSTALLED_APPS`` setting.

For example you might have::

    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.messages',
        'django.contrib.admin',
        'c5filemanager',
        # other apps...
    )

You **don't** have to run ``manage.py syncdb`` because ``django-c5filemanager``
doesn't use any models.

.. _urls:

URLs
----

Add the following line **before** the admin-urls::

    (r'^admin/c5filemanager/', include('c5filemanager.urls')),

So you might have::

    urlpatterns = patterns('',
        (r'^admin/c5filemanager/', include('c5filemanager.urls')),
        # Uncomment the next line to enable the admin:
        (r'^admin/', include(admin.site.urls)),
        # other URLs...
    )

Core Five Filemanager
---------------------

You need to use the following fork of the original Filemanager created by Core
Five: https://github.com/simogeo/Filemanager

Since there aren't releases we need to use a specific git revision. Last
revision, at the time of this writing, is:
``5e6bf11431b87b46e52840cf064a18a5a7cb7cba``.

Download
~~~~~~~~

You can use ``git``::

    $ git clone http://github.com/simogeo/Filemanager.git
    $ cd Filemanager
    $ git checkout 5e6bf11431b87b46e52840cf064a18a5a7cb7cba

Or the download page of GitHub:

https://github.com/simogeo/Filemanager/archive/5e6bf11431b87b46e52840cf064a18a5a7cb7cba.zip

Install
~~~~~~~

1. Copy or symlink the folder ``Filemanager`` inside your ``STATIC_ROOT`` and
   rename it to lower-case.

2. Create the ``upload`` directory inside ``MEDIA_ROOT``.

Inside ``STATIC_ROOT`` you might have::

    $ ls $YOUR_PROJECT_STATIC_ROOT
    css  filemanager  images

Configure
~~~~~~~~~

You have to edit two files: ``filemanager.config.js`` and
``filemanager.js``. Both will be in ``STATIC_ROOT/filemanager/scripts``.

filemanager.config.js
"""""""""""""""""""""

Inside ``STATIC_ROOT/filemanager/scripts`` rename the default
configuration file (``filemanager.config.js.default``) removing the .default
at the end of the filename.

The variable ``fileRoot`` must be set to ``MEDIA_URL/upload/``. You can change
other options according your needs.

Assuming your ``MEDIA_URL`` is::

    MEDIA_URL = '/media/'

You should have:

.. code-block:: javascript

    var fileRoot = '/media/upload/';

You can ignore (or delete):

.. code-block:: javascript

    var lang = 'php';

At this point, your ``STATIC_ROOT/filemanager/scripts/filemanager.config.js``
might be:

.. code-block:: javascript

    // Set culture to display localized messages
    var culture = 'en';

    // Autoload text in GUI
    var autoload = true;

    // Display full path - default : false
    var showFullPath = false;

    var am = document.location.pathname.substring(1, document.location.pathname
            .lastIndexOf('/') + 1);
    // Set this to the directory you wish to manage.
    var fileRoot = '/media/upload/';

    // Show image previews in grid views?
    var showThumbs = true;

filemanager.js
""""""""""""""

You have to change the ``fileConnector`` variable.

Assuming you are following :ref:`urls` subsection, change:

.. code-block:: javascript

    // Sets paths to connectors based on language selection.
    var fileConnector = 'connectors/' + lang + '/filemanager.' + lang;

in:

.. code-block:: javascript

    var fileConnector = '/admin/c5filemanager/';

How to use the file manager in Django admin site
------------------------------------------------

You can put a link to the file manager index using
`django-admin-tools <http://www.bitbucket.org/izi/django-admin-tools/>`_.

The file manager index will be at
``/STATIC_URL/C5FILEMANAGER_MEDIA/index.html``, see :ref:`available_settings`
for details.

Assuming you are following this document your link might be::

    /static/filemanager/index.html
