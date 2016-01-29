# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import json
import uuid
import mimetypes
import os
import re
from os import path
import StringIO
import paramiko
from contextlib import contextmanager
import itertools
from PIL import Image

from fs.osfs import OSFS
from fs.sftpfs import SFTPFS
from fs.mountfs import MountFS
from fs.wrapfs.readonlyfs import ReadOnlyFS

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden
from django.shortcuts import render
from django.utils.datastructures import SortedDict as OrderedDict
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.core.exceptions import PermissionDenied

from labs.models import Lab
from .decorators import filemanager_require_auth

encode_json = json.JSONEncoder().encode

try:
    from PIL import Image
except ImportError:
    raise EnvironmentError('Must have the PIL (Python Imaging Library).')

from django.conf import settings


normalize_path = os.path.normpath
absolute_path = os.path.abspath
split_path = os.path.split
split_ext = os.path.splitext


class FileManagerMixin(object):

    def dispatch(self, request, *args, **kwargs):
        self.UPLOAD_URL, self.UPLOAD_ROOT = self.get_upload(request, *args, **kwargs)
        self.lab = Lab.objects.get(pk=request.session.get('lab'))

        if not self.lab.is_assistant(request.user):
            raise PermissionDenied

    def smart_mount(self, file_path=None):
        """
        Mounts only fs which store file on file_path. If file_path isn't set mounts all fs.
        :param file_path: (string) relative path to the file(from a pyfs root)
        """
        self.fs = MountFS()
        local_fs = OSFS(self.UPLOAD_ROOT)
        self.fs.mountdir('.', local_fs)
        if not self.fs.exists(file_path) or not file_path:
            for storage in self.lab.storages.all():
                if file_path.startswith(storage.get_folder_name()) or not file_path:
                    try:
                        if storage.public_key:
                            pkey = paramiko.RSAKey.from_private_key(StringIO.StringIO(storage.public_key))
                            remote_fs = SFTPFS(connection=storage.host, username=storage.username, pkey=pkey, root_path=storage.get_path())
                        elif storage.password:
                            remote_fs = SFTPFS(connection=storage.host, username=storage.username, password=storage.password, root_path=storage.get_path())
                        # else raise
                        if storage.readonly:
                            remote_fs = ReadOnlyFS(remote_fs)

                        self.fs.mountdir(storage.get_folder_name(), remote_fs)
                    except:  # TODO: too broad, add logger
                        pass

    def get_upload(self, request, *args, **kwargs):
        lab = request.session.get('lab')
        if not lab:
            lab = unicode(Lab.objects.get(pk=kwargs.get('lab_pk')).id)
            request.session['lab'] = lab

        return os.path.join(settings.FILEMANAGER_UPLOAD_URL, lab + '/'), os.path.join(settings.FILEMANAGER_UPLOAD_ROOT, lab + '/')


def alternative_names(filename):
        base, ext = os.path.splitext(filename)
        for i in itertools.count(1):
            yield base + u"_%i" % i + ext


def trim_upload_url(url, UPLOAD_URL):
    assert url.startswith(UPLOAD_URL)
    return url[len(UPLOAD_URL):]


def valid_file_filter(file_name):
    if file_name[0] == '.':
        return False
    return True


def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)


def static_file(relative_url):
    return path.join(settings.STATIC_URL, 'filemanager', relative_url)


def check_directory(upload_root):
    """
    Backward compatibility. Some views from other apps use it.
    """
    if not os.path.exists(upload_root):
        os.makedirs(upload_root)


def get_upload(request, *args, **kwargs):
    """
    Backward compatibility. Some views from other apps use it.
    """
    lab = request.session.get('lab')
    if not lab:
        lab = unicode(Lab.objects.get(pk=kwargs.get('lab_pk')).id)
        request.session['lab'] = lab

    return os.path.join(settings.FILEMANAGER_UPLOAD_URL, lab + '/'), os.path.join(settings.FILEMANAGER_UPLOAD_ROOT, lab + '/')


#  TODO: Replace contextmanager with http response.(loose couplings)
@contextmanager
def pyfs_file_ang(lab_pk, file_path):
    """
    This context manager return file-like object from pyfs.
    Is used with angular filemanager.
    :param lab_pk: current lab.pk
    :param file_path: (string) relative path to the file(from a pyfs root)
    :return:
    """
    try:
        UPLOAD_ROOT = os.path.join(settings.FILEMANAGER_UPLOAD_ROOT, lab_pk + '/')
        relative_dir_path = file_path[1:]
        fs = MountFS()
        local_fs = OSFS(UPLOAD_ROOT)
        fs.mountdir('.', local_fs)
        lab = Lab.objects.get(pk=lab_pk)
        if not fs.exists(relative_dir_path):
            for storage in lab.storages.all():
                if relative_dir_path.startswith(storage.get_folder_name()):
                    try:
                        if storage.public_key:
                            pkey = paramiko.RSAKey.from_private_key(StringIO.StringIO(storage.public_key))
                            remote_fs = SFTPFS(connection=storage.host, username=storage.username, pkey=pkey, root_path=storage.get_path())
                        elif storage.password:
                            remote_fs = SFTPFS(connection=storage.host, username=storage.username, password=storage.password, root_path=storage.get_path())
                        # else raise
                        if storage.readonly:
                            remote_fs = ReadOnlyFS(remote_fs)
                        fs.mountdir(storage.get_folder_name(), remote_fs)
                    except:  #TODO: too broad, add logger
                        pass

        file_object = fs.open(relative_dir_path, 'rb')

        yield file_object
    finally:
        pass


class FileManagerDownloadView(FileManagerMixin, View):
    """
    Return response with a file from a pyfs

    """
    # TODO is it needed?
    def dispatch(self, request, *args, **kwargs):
        super(FileManagerDownloadView, self).dispatch(request, *args, **kwargs)
        fs_path = kwargs.get('fs_path')
        self.smart_mount(fs_path)

        content_type = mimetypes.guess_type(fs_path)[0]
        filename = smart_str(os.path.basename(fs_path))

        size = self.fs.getsize(fs_path)
        response = HttpResponse(content_type=content_type)
        response['Content-Length'] = size
        file_object = self.fs.open(fs_path, 'rb')
        response['Content-Disposition'] = u'attachment; filename={}'.format(filename.decode('utf-8'))
        response.write(file_object.read())
        return response


class AngularFileManagerMixin(object):

    def get_info(self, relative_info_path):
        """
        Return dict with meta info about a file.
        """
        info_path = path.join(self.UPLOAD_ROOT, relative_info_path)
        info_url = path.join(self.UPLOAD_URL, relative_info_path)

        _, name = split_path(info_url)

        if self.fs.isdir(relative_info_path):
            thefile = {
                "name": name,
                "type": "dir"
            }
        else:
            _, ext = split_ext(info_path)
            thefile = {
                "name": name,
                "type": "file"
            }

        file_metadata = self.fs.getinfo(relative_info_path)
        if file_metadata.get('created_time', ''):
            thefile['date'] = file_metadata.get('created_time').strftime('%Y-%m-%d %H:%M:%S')
        if file_metadata.get('modified_time', ''):
            thefile['date'] = file_metadata.get('modified_time').strftime('%Y-%m-%d %H:%M:%S')
        thefile['size'] = file_metadata.get('size')
        return thefile


class FileManagerBaseView(FileManagerMixin, View):
    """
    Render base filemanager template
    """
    @filemanager_require_auth
    def dispatch(self, request, *args, **kwargs):
        return render(request, kwargs.get('template_name', 'filemanager/base.html'))


class AngFileManagerListView(AngularFileManagerMixin, FileManagerMixin, View):
    """
    Return json response with content of directory.
    https://github.com/joni2back/angular-filemanager/blob/master/API.md - api description
    """
    @csrf_exempt
    @filemanager_require_auth
    def dispatch(self, request, *args, **kwargs):
        super(AngFileManagerListView, self).dispatch(request, *args, **kwargs)
        if request.method == 'POST':
            d = json.loads(request.body)
            relative_dir_path = d['params']['path'][1:]  # remove opening slash
            if not relative_dir_path:
                relative_dir_path = ''
            self.smart_mount(relative_dir_path)
            result = OrderedDict()
            result['result'] = []
            for filename in self.fs.listdir(relative_dir_path):
                relative_filename = path.join(relative_dir_path, filename)
                result['result'].append(self.get_info(relative_filename))
            return HttpResponse(encode_json(result))


class AngFileManagerCreateView(AngularFileManagerMixin, FileManagerMixin, View):
    """
    Create directory.
    https://github.com/joni2back/angular-filemanager/blob/master/API.md - api description
    """

    @csrf_exempt
    @filemanager_require_auth
    def dispatch(self, request, *args, **kwargs):
        super(AngFileManagerCreateView, self).dispatch(request, *args, **kwargs)
        if request.method == 'POST':
            d = json.loads(request.body)
            relative_dir_path = d['params']['path'][1:]  # remove opening slash
            folder_name = d['params']['name']
            if not relative_dir_path:
                relative_dir_path = ''
            self.smart_mount(relative_dir_path)

            new_path = path.join(relative_dir_path, folder_name)

            if self.fs.isdir(relative_dir_path):
                try:
                    self.fs.makedir(new_path)
                    success_code = True
                    error_message = None
                except:
                    error_message = 'There was an error creating the directory.'
                    success_code = None
            else:
                success_code = None
                error_message = 'There is no Root Directory.'

            result = OrderedDict()
            result['result'] = {'success': success_code, 'error': error_message}

            return HttpResponse(encode_json(result))


class AngFileManagerRenameView(AngularFileManagerMixin, FileManagerMixin, View):
    """
    Rename directory or file.
    https://github.com/joni2back/angular-filemanager/blob/master/API.md - api description
    """
    @csrf_exempt
    @filemanager_require_auth
    def dispatch(self, request, *args, **kwargs):
        super(AngFileManagerRenameView, self).dispatch(request, *args, **kwargs)
        if request.method == 'POST':
            d = json.loads(request.body)
            relative_dir_path = d['params']['path'][1:]  # remove opening slash
            new_path = d['params']['newPath']

            if not relative_dir_path:
                relative_dir_path = ''
            self.smart_mount(relative_dir_path)

            if self.fs.isdir(relative_dir_path):
                try:
                    self.fs.movedir(relative_dir_path, new_path)
                    success_code = True
                    error_message = None
                except:
                    error_message = 'There was an error renaming the directory.'
                    success_code = None
            else:
                try:
                    self.fs.move(relative_dir_path, new_path)
                    success_code = True
                    error_message = None
                except:
                    error_message = 'There was an error renaming the file.'
                    success_code = None

            result = OrderedDict()
            result['result'] = {'success': success_code, 'error': error_message}

            return HttpResponse(encode_json(result))


class AngFileManagerRemoveView(AngularFileManagerMixin, FileManagerMixin, View):
    """
    Remove directory or file.
    https://github.com/joni2back/angular-filemanager/blob/master/API.md - api description
    """
    @csrf_exempt
    @filemanager_require_auth
    def dispatch(self, request, *args, **kwargs):
        super(AngFileManagerRemoveView, self).dispatch(request, *args, **kwargs)
        if request.method == 'POST':
            d = json.loads(request.body)
            relative_dir_path = d['params']['path'][1:]  # remove opening slash

            self.smart_mount(relative_dir_path)

            if self.fs.isdir(relative_dir_path):
                try:
                    self.fs.removedir(relative_dir_path)
                    success_code = True
                    error_message = None
                except Exception as e:
                    print e
                    error_message = 'There was an error removing the directory.'
                    success_code = None
            else:
                try:
                    self.fs.remove(relative_dir_path)
                    success_code = True
                    error_message = None
                except:
                    error_message = 'There was an error removing the file.'
                    success_code = None

            result = OrderedDict()
            result['result'] = {'success': success_code, 'error': error_message}

            return HttpResponse(encode_json(result))


class AngFileManagerUploadView(AngularFileManagerMixin, FileManagerMixin, View):
    """
    Upload file to the directory.
    https://github.com/joni2back/angular-filemanager/blob/master/API.md - api description
    """
    @csrf_exempt
    @filemanager_require_auth
    def dispatch(self, request, *args, **kwargs):
        super(AngFileManagerUploadView, self).dispatch(request, *args, **kwargs)
        if request.method == 'POST':
            destination = request.POST['destination'][1:]
            self.smart_mount(destination)
            try:
                f = request.FILES.get('file-0', request.FILES.get('upload'))
                filename = f.name
                upload_file = path.join(destination, filename)
                self.smart_mount(upload_file)
                if self.fs.exists(upload_file):
                    filename = next(alt_name for alt_name in alternative_names(filename) if not self.fs.exists(path.join(destination, alt_name)))
                    upload_file = path.join(destination, filename)
                    # message = _('File with the same name already exists. The uploaded file has been renamed to \'{}\''.format(filename))

                destination = self.fs.open(upload_file, 'wb+')
                for chunk in f.chunks():
                    destination.write(chunk)
                destination.close()

                success_code = True
                error_message = None
            except:
                error_message = 'There was an error uploding the file.'
                success_code = None

            result = OrderedDict()
            result['result'] = {'success': success_code, 'error': error_message}

            return HttpResponse(encode_json(result))


class AngFileManagerDownloadView(AngularFileManagerMixin, FileManagerMixin, View):
    """
    Handle file downloading.
    https://github.com/joni2back/angular-filemanager/blob/master/API.md - api description
    """
    @csrf_exempt
    @filemanager_require_auth
    def dispatch(self, request, *args, **kwargs):
        super(AngFileManagerDownloadView, self).dispatch(request, *args, **kwargs)
        relative_dir_path = request.GET["path"][1:]
        self.smart_mount(relative_dir_path)
        download_path = path.join(self.UPLOAD_ROOT, relative_dir_path)
        content_type = mimetypes.guess_type(download_path)[0]
        filename = smart_str(os.path.basename(download_path))

        size = self.fs.getsize(relative_dir_path)
        response = HttpResponse(content_type=content_type)
        response['Content-Length'] = size
        file_object = self.fs.open(relative_dir_path, 'rb')
        response['Content-Disposition'] = u'attachment; filename={}'.format(filename.decode('utf-8'))
        response.write(file_object.read())
        return response


class SummernoteUploadView(View):
    """
    Handle image uploading from summernote wysiwyg.
    """
    def get_file_name(self, lab_pk, filename):
        """
        return file name for saving file. check for filename conflicts.
        Add random string to name if filename already exists.
        """
        path = os.path.join(settings.FILEMANAGER_UPLOAD_ROOT, lab_pk, filename)
        name = filename
        while os.path.isfile(path):
            name = u'{}_{}.{}'.format(
                filename.split('.')[0],
                uuid.uuid4().hex[:10],
                '.'.join(filename.split('.')[1:])
            )
            path = os.path.join(settings.FILEMANAGER_UPLOAD_ROOT, lab_pk, name)

        return name

    def dispatch(self, request, *args, **kwargs):
        if request.method != 'POST':
            return HttpResponseBadRequest('Only POST method is allowed')

        if not request.user.is_authenticated():
            return HttpResponseForbidden('Only authenticated users are allowed')

        if not request.FILES.getlist('files'):
            return HttpResponseBadRequest('No files were requested')

        try:
            attachments = []
            for file in request.FILES.getlist('files'):

                # check if an image
                try:
                    Image.open(file)
                except IOError:
                    return HttpResponseServerError('Failed to save attachment. Not an Image')

                filename = self.get_file_name(kwargs.get('lab_pk'), file.name)
                path = os.path.join(settings.FILEMANAGER_UPLOAD_ROOT, kwargs.get('lab_pk'), filename)

                with open(path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)

                url = request.build_absolute_uri(os.path.join(
                    settings.FILEMANAGER_UPLOAD_URL,
                    kwargs.get('lab_pk'),
                    filename,
                ))

                attachments.append({
                    'name': filename,
                    'size': file.size,
                    'url': url,
                })

            return HttpResponse(encode_json({
                'files': attachments
            }))

        except IOError:
            return HttpResponseServerError('Failed to save attachment')


# TODO: add stubs for get methods