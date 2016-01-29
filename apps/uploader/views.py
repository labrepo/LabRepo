# -*- coding: utf-8 -*-
import os
import json
import requests
import mimetypes
import StringIO
import logging

from PIL import Image, ImageDraw
import ghostscript

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.temp import NamedTemporaryFile
from django.core.files import File
from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import StreamingHttpResponse
from django.core.servers.basehttp import FileWrapper
from django.core.exceptions import PermissionDenied
from django.apps import apps

from filemanager.views import pyfs_file_ang
from .response import JSONResponse, response_mimetype
from .serialize import serialize


logger = logging.getLogger(__name__)


class BaseUploaderMixin(View, SingleObjectMixin):
    """
    Base class for file upload mixins
    """
    bind = True
    parent_model = None
    #field = 'files'

    def get_object(self, queryset=None):
        """
        Return the parent model of file
        """
        pk = self.kwargs.get(self.pk_url_kwarg, None)

        try:
            parent = self.parent_model.objects.get(pk=pk)
            return parent
        except ObjectDoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        """
        Return serializated list of object files
        """
        files = []
        if self.get_object():
            parent = self.get_object()
            files_objs = self.model.objects.filter(parent=parent)
            files = [serialize(obj, lab_pk=self.kwargs.get('lab_pk')) for obj in files_objs]

        data = {'files': files}
        response = JSONResponse(data, mimetype=response_mimetype(self.request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response

    def generate_thumb(self, instance):
        """
        Generate thubnail for file. If file isn't image raise IOError, you must handle it.
        instance - BaseFile(or subclass) instance
        """
        img = Image.open(instance.file)
        img.thumbnail((256, 256))
        thumb_io = StringIO.StringIO()
        image_format = instance.filename.split('.')[-1].upper()
        if image_format == 'JPG':
            image_format = 'JPEG'
        img.save(thumb_io, format=image_format)

        thumb_file = InMemoryUploadedFile(thumb_io, None, u'thumb_{}'.format(instance.filename), instance.content_type,
                                          thumb_io.len, None)
        return thumb_file

    def generate_pdf_review(self, instance):
        """
        Generate thumbnail jpeg for pdf file.
        instance - BaseFile(or subclass) instance
        Return path to file with jpeg
        """
        filename_jpg = '/tmp/tmpjpg_{}.jpg'.format(instance.filename)
        try:
            # test.py just placeholder
            args = """test.py
                   -sDEVICE=jpeg
                   -o {}
                   -dJPEGQ=95
                   -dFirstPage=1
                   -dLastPage=1
                   {} """.format(filename_jpg, instance.file.path).split()

            GS = ghostscript.Ghostscript(*args)
            return filename_jpg

        except Exception as e:
            logger.exception("Fatal error while a pdf preview file generation")
            width = 330
            height = 490
            image = Image.new('RGB', (width, height), color=(255, 255, 255, 0))
            draw = ImageDraw.Draw(image)
            text = 'PDF preview error'.format(instance.filename)
            textwidth, textheight = draw.textsize(text)
            if textwidth < width and textheight < height:
                texttop = (height - textheight) // 2
                textleft = (width - textwidth) // 2
                draw.text((textleft, texttop), text, fill=(0, 0, 0))
            image.save(filename_jpg, 'JPEG')
            return filename_jpg


class FileUploadMixinView(BaseUploaderMixin):
    """
    Handles uploading file from client's local filesystem
    """

    def post(self, request,  *args, **kwargs):

        response_data = []

        if self.get_object():
            parent = self.get_object()

            for key, f in request.FILES.items():
                obj = self.model(parent=parent, file=f, content_type=f.content_type)
                obj.save()
                if f.content_type == 'application/pdf':
                    thumb_filename = self.generate_pdf_review(obj)
                    with open(thumb_filename, 'r') as tfile:
                        thumb_file = File(tfile)
                        obj.thumbnail.save(thumb_filename, thumb_file, True)
                    os.remove(thumb_filename)
                else:
                    #generate thumb
                    try:
                        thumb_file = self.generate_thumb(obj)
                        obj.thumbnail.save(thumb_file.name, thumb_file, True)
                    except IOError:
                        pass  # file isn't a image

                obj.save()

                response_data.append(serialize(obj, lab_pk=self.kwargs.get('lab_pk')))

        data = {'files': response_data}
        response = JSONResponse(data, mimetype=response_mimetype(request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response


class DropboxFileUploadMixinView(BaseUploaderMixin):
    """
    Handles uploading file from dropbox
    """

    def post(self, request,  *args, **kwargs):

        parent = self.get_object()
        files = json.loads(request.POST.get('files[]'))
        need_upload = request.POST.get('need_upload') == 'true'

        for f in files:
            obj = self.model(parent=parent)

            if need_upload:
                r = requests.get(f.get('link'), stream=True)
                img_temp = NamedTemporaryFile(delete=True)
                for chunk in r.iter_content(8192):
                    img_temp.write(chunk)
                obj.file.save(f.get('name'), File(img_temp))
                img_temp.flush()

                link = f.get('thumbnailLink').replace('bounding_box=75', 'bounding_box=256')
                r = requests.get(link, stream=True)
                if f.get('thumbnailLink'):
                    img_temp = NamedTemporaryFile(delete=True)
                    for chunk in r.iter_content(8192):
                        img_temp.write(chunk)
                    obj.thumbnail.save(f.get('name'), File(img_temp))
                    img_temp.flush()

            if f.get('thumbnailLink'):
                obj.outer_thumbnail_url = f.get('thumbnailLink')
            obj.content_type = mimetypes.guess_type(f.get('name'))[0]  # or 'image/png',
            obj.outer_url = f.get('link')
            obj.save()

        response = JSONResponse({'status': 'ok'}, mimetype=response_mimetype(request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response


class LocalFileUploadMixinView(BaseUploaderMixin):
    """
    Handles uploading file from labrepo server(sftp)
    """

    def post(self, request,  *args, **kwargs):

        parent = self.get_object()
        files = json.loads(request.POST.get('files[]'))
        need_upload = request.POST.get('need_upload') == 'true'

        for f in files:
            obj = self.model(parent=parent)
            obj.content_type = mimetypes.guess_type(f.get('name'))[0]  # or 'image/png',

            if need_upload:
                with pyfs_file_ang(kwargs.get('lab_pk'), f.get('link')) as file_obj:
                    obj.file.save(f.get('name'), File(file_obj))
                obj.save()
                #generate thumb
                if obj.content_type == 'application/pdf':
                    thumb_filename = self.generate_pdf_review(obj)
                    with open(thumb_filename, 'r') as f_tmp:
                        thumb_file = File(f_tmp)
                        obj.thumbnail.save(thumb_filename, thumb_file, True)
                    os.remove(thumb_filename)
                else:
                    try:
                        thumb_file = self.generate_thumb(obj)
                        obj.thumbnail.save(thumb_file.name, thumb_file, True)
                    except IOError:
                        pass  # file isn't a image

            if f.get('thumbnailLink'):
                obj.outer_thumbnail_url = f.get('thumbnailLink')

            obj.outer_url = f.get('link')
            obj.save()

        response = JSONResponse({'status': 'ok'}, mimetype=response_mimetype(request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response


class FileDeleteView(View):
    """
    Delete file instance
    """

    def delete(self, request, *args, **kwargs):
        model_type = apps.get_model(app_label=kwargs['app_name'], model_name=kwargs['model_name'])
        obj = model_type.objects.get(pk=kwargs['pk'])

        if not obj.parent.is_owner(request.user):
            raise PermissionDenied
        obj.delete()

        response = JSONResponse(True, mimetype=response_mimetype(request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response