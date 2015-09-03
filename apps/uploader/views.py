# encoding: utf-8
import json
import requests
import mimetypes

# from django.apps import apps
from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import StreamingHttpResponse, HttpResponse
from django.core.servers.basehttp import FileWrapper

from mongoengine.base.common import get_document

from .response import JSONResponse, response_mimetype
from .serialize import serialize


class FileUploadMixinView(View, SingleObjectMixin):

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

    def post(self, request,  *args, **kwargs):

        response_data = []

        if self.get_object():
            parent = self.get_object()

            for key, file in request.FILES.items():
                obj = self.model(parent=parent, name=file.name, content_type=file.content_type)
                obj.file.put(file, content_type=file.content_type)
                obj.size = obj.file.get().length
                obj.save()

                response_data.append(serialize(obj, lab_pk=self.kwargs.get('lab_pk')))

        data = {'files': response_data}
        response = JSONResponse(data, mimetype=response_mimetype(request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response

    def get(self, request, *args, **kwargs):
        files = []
        if self.get_object():
            parent = self.get_object()
            files_objs = self.model.objects.filter(parent=parent)
            files = [serialize(obj, lab_pk=self.kwargs.get('lab_pk')) for obj in files_objs]

        data = {'files': files}
        response = JSONResponse(data, mimetype=response_mimetype(self.request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response


class DropboxFileUploadMixinView(View, SingleObjectMixin):

    bind = True
    parent_model = None
    #field = 'files'

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg, None)

        try:
            parent = self.parent_model.objects.get(pk=pk)
            return parent
        except ObjectDoesNotExist:
            return None

    def post(self, request,  *args, **kwargs):

        parent = self.get_object()
        files = json.loads(request.POST.get('files[]'))
        need_upload = request.POST.get('need_upload') == 'true'

        for f in files:
            obj = self.model(parent=parent)

            if need_upload:
                r = requests.get(f.get('link'), stream=True)
                obj.file.new_file()
                for chunk in r.iter_content(8192):
                    obj.file.write(chunk)
                obj.file.close()
            obj.size = f.get('bytes')  # May be wrong, get it from mongo
            obj.content_type = mimetypes.guess_type(f.get('name'))[0]# or 'image/png',
            obj.name = f.get('name')
            obj.outer_url = f.get('link')
            obj.save(user=request.user)

        response = JSONResponse({'status': 'ok'}, mimetype=response_mimetype(self.request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response


class FileDeleteView(View):
    """
    Delete instance
    """
    # TODO: security
    def delete(self, request, *args, **kwargs):

        obj = get_document(kwargs['document_name']).objects.get(pk=kwargs['pk'])
        obj.delete()

        response = JSONResponse(True, mimetype=response_mimetype(request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response


class DownloadFileView(View):
    """
    Send file to browser.
    """
    # TODO: security
    def get(self, request, *args, **kwargs):
        obj = get_document(kwargs['document_name']).objects.get(pk=kwargs['pk'])

        chunk_size = 8192
        response = StreamingHttpResponse(FileWrapper(obj.file.get(), chunk_size),
                                        content_type=obj.content_type)
        response['Content-Length'] = obj.size
        response['Content-Disposition'] = "attachment; filename=%s" % obj.name
        return response