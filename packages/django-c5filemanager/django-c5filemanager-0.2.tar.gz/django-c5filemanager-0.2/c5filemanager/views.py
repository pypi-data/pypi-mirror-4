# -*- coding: utf-8 -*-
"""c5filemanager.views module.

THIS SOFTWARE IS UNDER BSD LICENSE.
Copyright (c) 2010-2012 Daniele Tricoli <eriol@mornie.org>

Read LICENSE for more informations.
"""
import os
import posixpath
import shutil
import time
import urllib

import Image

from django.contrib.admin.views.decorators import staff_member_required
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse
from django.utils import simplejson
# For OrderedDict is needed simplejson >= 2.1.0
from django.utils.simplejson import OrderedDict
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt

from c5filemanager import settings

IMAGES_EXT = ('jpg', 'jpeg', 'gif', 'png')
PREVIEW_IMAGES_PATH = 'images/fileicons/'
PREVIEW_IMAGES = {
    'Directory': PREVIEW_IMAGES_PATH + '_Open.png',
    'Default': PREVIEW_IMAGES_PATH + 'default.png',
    'Image': PREVIEW_IMAGES_PATH + '%s.png'
}

TIME_FORMAT = '%Y/%m/%d - %H:%M:%S'

def norm_path_list(path):
    """Normalize the path and return a list of each part."""
    path = posixpath.normpath(urllib.unquote(path))
    path = path.lstrip('/')
    return path.split('/')

def get_path(requested_path):
    """Return the real path of a file (or directory) inside MEDIA_ROOT."""

    def _clean_equal(element1, element2):
        """
        Return an empty string if the passed elements are equal, the second one
        if the first is None.

        It's used with the map() below to clean requested_path deleting those
        parts of the splitted URL that belong to settings.UPLOAD_DIRECTORY_URL.
        """
        if element1 == element2:
            return ''
        if element1 is None and element2:
            return element2

    new_path = '/'.join(map(_clean_equal,
                    norm_path_list(settings.UPLOAD_DIRECTORY_URL),
                    norm_path_list(requested_path)))
    new_path = new_path.lstrip('/')

    return os.path.join(settings.MEDIA_ROOT,
                        settings.UPLOAD_DIRECTORY,
                        new_path)

def create_file_info_for(requested_path, real_path, show_thumbs=True):
    """Fill proper file information needed by Code Five Filemanager."""
    file_info = {
        'Path': '',
        'Filename': '',
        'File Type': '',
        'Preview': '',
        'Properties': {
            'Date Created': '',
            'Date Modified': '',
            'Height': '',
            'Width': '',
            'Size': ''
        },
        'Error': '',
        'Code': 0
    }

    if os.path.exists(real_path):
        file_info['Path'] = requested_path
        file_info['Filename'] = os.path.basename(real_path)
        # Handle file extension: if ``path'' is a directory must be set to
        # 'dir', if absent or unknown to 'txt'.
        if os.path.isdir(real_path):
            ext = 'dir'
            file_info['Path'] = file_info['Path'] + '/'
            preview = PREVIEW_IMAGES['Directory']
        else:
            ext = os.path.splitext(real_path)[1][1:].lower()
            if not ext:
                ext = 'txt'
                preview = PREVIEW_IMAGES['Default']
            else:
                preview = PREVIEW_IMAGES['Image'] % ext
                # Check if the icon for the specified extension exists.
                preview_file_path = os.path.join(settings.MEDIA_ROOT,
                                        settings.C5FILEMANAGER_MEDIA,
                                        preview)
                if not os.path.exists(preview_file_path):
                    preview = PREVIEW_IMAGES['Default']
        file_info['File Type'] = ext
        file_info['Properties']['Date Created'] = time.strftime(TIME_FORMAT,
            time.localtime(os.path.getctime(real_path)))
        file_info['Properties']['Date Modified'] = time.strftime(TIME_FORMAT,
            time.localtime(os.path.getmtime(real_path)))
        if ext in IMAGES_EXT:
            img = Image.open(real_path)
            width, height = img.size
            file_info['Properties']['Height'] = height
            file_info['Properties']['Width'] = width
            if show_thumbs:
                preview = requested_path
        file_info['Preview'] = preview
        file_info['Properties']['Size'] = os.path.getsize(real_path)
    else:
        return error(_('No such file or directory.'))

    return file_info

def error(message, code=-1):
    """Return an error with the specified message and code."""
    err = {'Error': message, 'Code': code}
    return err

def getinfo(request):
    """Return information about a file."""
    requested_path = request.GET.get('path', None)

    real_path = get_path(requested_path)
    file_info = create_file_info_for(requested_path, real_path)

    return HttpResponse(simplejson.dumps(file_info),
                        mimetype='application/json')

def getfolder(request):
    """Return the collected info about all the files inside a directory."""
    requested_path = request.GET.get('path', None)
    show_thumbs = simplejson.loads(request.GET.get('showThumbs', 'null'))

    real_path = get_path(requested_path)

    # An ordered dict to collect info for all the files in the directory
    # pointed by ``path''
    files_info = OrderedDict()
    if os.path.isdir(real_path):
        for filename in sorted(os.listdir(real_path)):
            requested_file_path = os.path.join(requested_path, filename)
            real_file_path = os.path.join(real_path, filename)
            files_info[filename] = create_file_info_for(requested_file_path,
                                                        real_file_path,
                                                        show_thumbs)
    else:
        files_info = error(
            _('Directory %(path)s does not exist.') % {'path': requested_path})

    return HttpResponse(simplejson.dumps(files_info),
                        mimetype='application/json')


def rename(request):
    """Rename a file or directory."""
    old_path = request.GET.get('old', None)
    new_path = request.GET.get('new', None)
    response = {}

    old_file = get_path(old_path)

    if os.path.exists(old_file):
        old_name = os.path.basename(old_file)
        old_path_dir = os.path.dirname(old_file)
        # Using rename to move a file is not allowed so any directory
        # will be stripped.
        new_name = os.path.basename(new_path)
        new_file = os.path.join(old_path_dir, new_name)
        try:
            shutil.move(old_file, os.path.join(old_path_dir, new_name))
        except:
            response = error(_('Can\'t rename %(name)s.') % {'name': old_name})
        else:
            response['Code'] = 0
            response['Error'] = 'No Error'
            response['Old Path'] = old_file
            response['Old Name'] = old_name
            response['New Path'] = new_file
            response['New Name'] = new_name
    else:
        response = error(_('No such file or directory.'))

    return HttpResponse(simplejson.dumps(response),
                        mimetype='application/json')

def delete(request):
    """Delete a file."""
    requested_path = request.GET.get('path', None)
    file_to_be_deleted = get_path(requested_path)
    response = {}

    if os.path.exists(file_to_be_deleted):
        try:
            if os.path.isdir(file_to_be_deleted):
                os.rmdir(file_to_be_deleted)
            else:
                os.remove(file_to_be_deleted)
        except:
            response = error(
                _('Can\'t delete %(path)s.') % {'path': requested_path})
        else:
            response['Code'] = 0
            response['Error'] = 'No Error'
            response['Path'] = requested_path
    else:
        response = error(_('No such file or directory.'))

    return HttpResponse(simplejson.dumps(response),
                        mimetype='application/json')

def add(request):
    """Add a new file."""
    requested_path = request.POST.get('currentpath', None)
    new_file = request.FILES['newfile']
    response = {}
    try:
        handle_uploaded_file(requested_path, new_file)
    except:
        response = error(_('Can\'t add %(file)s.') % {'file': new_file.name})
    else:
        response['Path'] = requested_path
        response['Name'] = new_file.name
        response['Code'] = 0
        response['Error'] = 'No Error'
    html = '<textarea>' + simplejson.dumps(response) + '</textarea>'
    return HttpResponse(html)

def addfolder(request):
    """Add a new directory."""
    requested_path = request.GET.get('path', None)
    dir_name = request.GET.get('name', None)
    response = {}
    real_path = get_path(requested_path)
    try:
        os.mkdir(os.path.join(real_path, dir_name))
    except:
        path = os.path.join(requested_path, dir_name)
        response = error(
            _('Can\'t create %(path)s.') % {'path': path})
    else:
        response['Code'] = 0
        response['Error'] = 'No Error'
        response['Parent'] = requested_path
        response['Name'] = dir_name

    return HttpResponse(simplejson.dumps(response),
                        mimetype='application/json')

def download(request):
    """Download a file."""
    requested_path = request.GET.get('path', None)
    real_path = get_path(requested_path)
    filename = os.path.basename(real_path)
    response = HttpResponse(FileWrapper(file(real_path)),
                            content_type='application/x-download')
    response['Content-Length'] = os.path.getsize(real_path)
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response

handlers = {
    'getinfo': getinfo,
    'getfolder': getfolder,
    'rename': rename,
    'delete': delete,
    'addfolder': addfolder,
    'download': download
}

def handle_uploaded_file(path, f):
    """Handle an uploaded file."""
    real_path = get_path(path)
    new_file = os.path.join(real_path, f.name)
    try:
        destination = open(new_file, 'wb+')
        for chunk in f.chunks():
            destination.write(chunk)
    except IOError:
        raise
    finally:
        destination.close()

@csrf_exempt
@staff_member_required
def filemanager(request):
    """Connector for Code Five Filemanager."""
    if request.method == 'GET':
        mode = request.GET.get('mode', None)
        if mode is not None:
            callback = handlers[mode]
    elif request.method == 'POST':
        return add(request)

    return callback(request)
