# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import
import json
import mimetypes
import os
import re
import time
import shutil
from os import path

from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.datastructures import SortedDict as OrderedDict
from django.utils.encoding import smart_str
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
import itertools

from .decorators import filemanager_require_auth
from labs.documents import Lab


encode_json = json.JSONEncoder().encode

try:
    from PIL import Image
except ImportError:
    raise EnvironmentError('Must have the PIL (Python Imaging Library).')

from django.conf import settings


path_exists = os.path.exists
normalize_path = os.path.normpath
absolute_path = os.path.abspath
split_path = os.path.split
split_ext = os.path.splitext


def get_upload(request, *args, **kwargs):
    lab = request.session.get('lab')
    if not lab:
        lab = unicode(Lab.objects.get(pk=kwargs.get('lab_pk')).id)
        request.session['lab'] = lab
    return os.path.join(settings.FILEMANAGER_UPLOAD_URL, lab + '/'), os.path.join(settings.FILEMANAGER_UPLOAD_ROOT, lab + '/')


def check_directory(upload_root):
    if not path_exists(upload_root):
        os.makedirs(upload_root)


def trim_upload_url(url, UPLOAD_URL):
    assert url.startswith(UPLOAD_URL)
    return url[len(UPLOAD_URL):]


def valid_file_filter(file_name):
    if file_name[0] == '.':
        return False
    return True


def filename_list(base_dir):
    filenames = os.listdir(base_dir)
    valid_filenames = filter(valid_file_filter, filenames)
    nicely_sorted_filenames = natural_sort(valid_filenames)

    isnt_dir = lambda filename: not path.isdir(path.join(base_dir, filename))
    dirs_first_filenames = sorted(nicely_sorted_filenames, key=isnt_dir)

    return dirs_first_filenames


def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)


def static_file(relative_url):
    return path.join(settings.STATIC_URL, 'filemanager', relative_url)


def filetree(request, *args, **kwargs):
    UPLOAD_URL, UPLOAD_ROOT = get_upload(request, *args, **kwargs)
    output = ['<ul class="jqueryFileTree" style="display: none;">']
    relative_dir_path = trim_upload_url(request.POST.get('dir', ''), UPLOAD_URL)

    try:
        output = ['<ul class="jqueryFileTree" style="display: none;">']
        dir_path = path.join(UPLOAD_ROOT, relative_dir_path)
        dir_url = path.join(UPLOAD_URL, relative_dir_path)

        for filename in filename_list(dir_path):
            file_path = os.path.join(dir_path, filename)
            file_url = os.path.join(dir_url, filename)

            if os.path.isdir(file_path):
                output.append('<li class="directory collapsed"><a href="#" rel="%s/">%s</a></li>' % (file_url, filename))
            else:
                ext = os.path.splitext(filename)[1][1:]
                output.append('<li class="file ext_%s"><a href="#" rel="%s">%s</a></li>' % (ext, file_url, filename))

        output.append('</ul>')
    except Exception:
        pass

    output.append('</ul>')

    request.session["upload_path"] = relative_dir_path

    return HttpResponse(''.join(output))


def get_info(request, relative_info_path, *args, **kwargs):
    UPLOAD_URL, UPLOAD_ROOT = get_upload(request, *args, **kwargs)
    info_path = path.join(UPLOAD_ROOT, relative_info_path)
    info_url = path.join(UPLOAD_URL, relative_info_path)

    imagetypes = ['.gif', '.jpg', '.jpeg', '.png']
    if os.path.isdir(info_path):
        _, name = split_path(info_url)
        thefile = {
            'Path': info_url + "/",
            'Filename': name,
            'File Type': 'dir',
            'Preview': static_file('images/fileicons/_Open.png'),
            'Properties': {
                'Date Created': '',
                'Date Modified': '',
                'Width': '',
                'Height': '',
                'Size': ''
            },
            'Return': info_url,
            'Error': '',
            'Code': 0,
        }
    else:
        _, ext = split_ext(info_path)
        preview = static_file('images/fileicons/' + ext[1:] + '.png')
        thefile = {
            'Path': info_url,
            'Filename': split_path(info_path)[-1],
            'File Type': split_path(info_path)[1][1:],
            'Preview': preview,
            'Properties': {
                'Date Created': '',
                'Date Modified': '',
                'Width': '',
                'Height': '',
                'Size': ''
            },
            'Return': info_url,
            'Error': '',
            'Code': 0,
        }
        if ext in imagetypes:
            try:
                img = Image.open(open(info_path, "r"))
                xsize, ysize = img.size
                thefile['Properties']['Width'] = xsize
                thefile['Properties']['Height'] = ysize
                thefile['Preview'] = info_url
            except:
                pass

        thefile['File Type'] = os.path.splitext(info_path)[1][1:]
        thefile['Properties']['Date Created'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getctime(info_path)))
        thefile['Properties']['Date Modified'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(info_path)))
        thefile['Properties']['Size'] = os.path.getsize(info_path)
    return thefile


def alternative_names(filename):
    base, ext = os.path.splitext(filename)
    for i in itertools.count(1):
        yield base + "_%i" % i + ext


def handle_uploaded_file(request, f, *args, **kwargs):
    UPLOAD_URL, UPLOAD_ROOT = get_upload(request, *args, **kwargs)
    filename = f.name
    message = ''
    relative_upload_dir = request.session.get("upload_path", '')
    upload_url = path.join(UPLOAD_URL, relative_upload_dir)
    upload_dir = path.join(UPLOAD_ROOT, relative_upload_dir)
    upload_file = path.join(upload_dir, filename)

    if path_exists(upload_file):
        filename = next(alt_name for alt_name in alternative_names(filename) if not path_exists(path.join(upload_dir, alt_name)))
        upload_file = path.join(upload_dir, filename)
        message = _('File with the same name already exists. The uploaded file has been renamed to \'{}\''.format(filename))

    destination = open(upload_file, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
    if request.FILES.get('upload'):
        return mark_safe('<script type="text/javascript">window.parent.CKEDITOR.tools.callFunction({}, "{}", "{}");</script>'
                         .format(request.GET.get('CKEditorFuncNum', 0), upload_url + filename, message))
    result = {
        'Name': filename,
        'Path': upload_url,
        'Code': "0",
        'Error': ""
    }
    return '<textarea>' + encode_json(result) + '</textarea>'


@csrf_exempt
@filemanager_require_auth
def handler(request, *args, **kwargs):
    UPLOAD_URL, UPLOAD_ROOT = get_upload(request, *args, **kwargs)
    check_directory(UPLOAD_ROOT)
    if request.method == "POST":
        if request.GET.get('mode', None) == 'filetree':
            return filetree(request)
        try:
            result = handle_uploaded_file(request, request.FILES.get('newfile', request.FILES.get('upload')))
            return HttpResponse(result)
        except:
            pass
    else:

        if 'mode' not in request.GET:
            return render(request, kwargs.get('template_name', 'filemanager/index.html'), {
                'UPLOAD_URL': UPLOAD_URL})

        if request.GET["mode"] == "getinfo":
            info_url = request.GET["path"]
            relative_info_path = trim_upload_url(info_url, UPLOAD_URL)
            info_path = path.join(UPLOAD_ROOT, relative_info_path)

            return HttpResponse(encode_json(get_info(request, relative_info_path)))

        if request.GET["mode"] == "getfolder":
            dir_url = request.GET["path"]
            relative_dir_path = trim_upload_url(dir_url, UPLOAD_URL)
            dir_path = path.join(UPLOAD_ROOT, relative_dir_path)

            result = OrderedDict()
            request.session["upload_path"] = relative_dir_path

            for filename in filename_list(dir_path):
                relative_filename = path.join(relative_dir_path, filename)
                file_url = path.join(dir_url, filename)

                info = get_info(request, relative_filename)
                result[file_url] = info

            return HttpResponse(encode_json(result))

        if request.GET["mode"] == "rename":
            old_url = request.GET["old"]
            if old_url[-1] == '/':
                old_url = old_url[:-1]
            old_relative_file = trim_upload_url(old_url, UPLOAD_URL)
            base_relative_path = path.dirname(old_relative_file)
            base_url = path.join(UPLOAD_URL, base_relative_path)
            old_name = path.basename(old_url)
            old_file = path.join(UPLOAD_ROOT, old_relative_file)
            new_name = path.basename(request.GET["new"])
            new_file = path.join(UPLOAD_ROOT, base_relative_path, new_name)

            try:
                os.rename(old_file, new_file)
                error_message = new_name
                success_code = "0"
            except:
                success_code = "500"
                error_message = "There was an error renaming the file."

            if path.isdir(new_file):
                old_file += '/'
                new_file += '/'

            result = {
                'Old Path': base_url + "/",
                'Old Name': old_name,
                'New Path': base_url + "/",
                'New Name': new_name,
                'Error': error_message,
                'Code': success_code
            }

            return HttpResponse(encode_json(result))

        if request.GET["mode"] == "delete":
            delete_url = request.GET["path"]
            relative_delete_path = trim_upload_url(delete_url, UPLOAD_URL)
            delete_path = path.join(UPLOAD_ROOT, relative_delete_path)
            name = ''
            try:
                directory, name = path.split(delete_path)
                if path.isdir(delete_path + "/"):
                    shutil.rmtree(delete_path)
                else:
                    os.remove(delete_path)

                error_message = name + ' was deleted successfully.'
                success_code = "0"
            except:
                error_message = "There was an error deleting the file. <br/> The operation was either not " \
                                "permitted or it may have already been deleted."
                success_code = "500"

            result = {
                'Path': delete_url,
                'Name': name,
                'Error': error_message,
                'Code': success_code
            }
            return HttpResponse(encode_json(result))

        if request.GET["mode"] == "addfolder":
            base_url = request.GET['path']
            relative_path = trim_upload_url(base_url, UPLOAD_URL)
            base_path = path.join(UPLOAD_ROOT, relative_path)

            name = unicode(request.GET["name"].replace(" ", "_"))

            new_path = path.join(base_path, name)
            new_url = path.join(base_url, name)

            if path_exists(base_path):
                try:
                    os.mkdir(new_path)
                    success_code = "0"
                    error_message = 'Successfully created folder.'
                except:
                    error_message = 'There was an error creating the directory.'
                    success_code = "500"
            else:
                success_code = "500"
                error_message = 'There is no Root Directory.'

            result = {
                'Path': base_url,
                'Parent': base_url,
                'Name': name,
                'New Path': new_url,
                'Error': error_message,
                'Code': success_code
            }
            return HttpResponse(encode_json(result))

        if request.GET["mode"] == "download":
            relative_dir_path = trim_upload_url(request.GET["path"], UPLOAD_URL)
            download_path = path.join(UPLOAD_ROOT, relative_dir_path)
            content_type = mimetypes.guess_type(download_path)[0]
            filename = smart_str(os.path.basename(download_path))
            wrapper = FileWrapper(file(download_path, 'rb'))
            size = os.path.getsize(download_path)

            # Create the HttpResponse object with the appropriate headers.
            response = HttpResponse(wrapper, content_type=content_type)
            response['Content-Length'] = size
            response['Content-Disposition'] = u'attachment; filename="{}"'.format(filename)
            return response
    return HttpResponse("failed")
