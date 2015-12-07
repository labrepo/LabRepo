# -*- coding: utf-8 -*-
import json
import logging

import bs4
import requests
from urlparse import urlparse

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.views.generic import View, DeleteView, UpdateView, DetailView
from django.views.generic.edit import ModelFormMixin
from django.views.generic.list import BaseListView, MultipleObjectTemplateResponseMixin
from django.views.generic.detail import SingleObjectMixin
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import formats
from django.core import serializers

from preserialize.serialize import serialize  # todo change with drf serizlizer

from django.db.models import Q

from common.decorators import get_obj_or_404
from common.mixins import (ActiveTabMixin, LoginRequiredMixin, AjaxableResponseMixin,
                           RecentActivityMixin, CheckViewPermissionMixin, CommentMixin, DataMixin, JsTreeMixin,
                           InitialLabMixin)
# from common.serializer import JsonDocumentEncoder
from uploader.views import FileUploadMixinView, DropboxFileUploadMixinView, LocalFileUploadMixinView
from dashboard.models import RecentActivity
from .models import Unit, UnitFile, UnitLink
from experiments.models import Experiment
from .forms import UnitForm, UnitUpdateForm, UnitTabForm
from labs.models import Lab
from tags.models import Tag
# from unit_collections.models import Collection

logger = logging.getLogger(__name__)


class UnitCreateView(LoginRequiredMixin, JsTreeMixin, ModelFormMixin, MultipleObjectTemplateResponseMixin,
                     BaseListView, View):
    """
     View for creating a new unit
    """
    model = Unit
    form_class = UnitForm
    update_form_class = UnitUpdateForm
    template_name = 'units/unit_list.html'
    active_tab = 'units'
    title = {
        'pk': 'pk', 'sample': 'sample', 'experiments_pk': 'experiments', 'parent_pk': 'parent', 'tags_pk': 'tags',
        'change reasons': 'comment',
    }
    title_fields = ['pk', 'sample', 'experiments', 'parent', 'tags', 'readonly']
    extra_title = ['change reasons', 'experiments_pk', 'parent_pk', 'tags_pk']
    headers = ['pk', ugettext('sample'), ugettext('experiments'), ugettext('parents'), ugettext('tags'), 'readonly',
               ugettext('change reasons'), 'experiments_pk', 'parent_pk', 'tags_pk']

    @method_decorator(get_obj_or_404)
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.lab = self.lab
        user = self.request.user
        if not (self.object.is_member(user) or self.object.is_owner(user)):
            return {'errors': {'non_field_error': 'Permission denied'}, 'success': False}
        # self.object = self.object.save(user=self.request.user, revision_comment=form.cleaned_data.get('comment'))
        self.object = self.object.save()
        self.save_recent_activity(self.flag, unit=self.object.pk,
                                  experiment=[unicode(obj.pk) for obj in self.object.experiments])
        return {'pk': unicode(self.object.pk), 'success': True}

    @method_decorator(login_required)
    @method_decorator(get_obj_or_404)
    def dispatch(self, *args, **kwargs):
        self.user = self.request.user
        self.lab = Lab.objects.get(pk=self.kwargs.get('lab_pk'))
        if not self.lab.is_assistant(self.request.user):
            raise PermissionDenied
        return super(UnitCreateView, self).dispatch(*args, **kwargs)

    def get_experiments(self):
        experiments = Experiment.objects.filter(lab=self.lab, active=True)
        if self.lab.is_guest(self.user):
            experiments = experiments.filter(Q(owners=self.user) | Q(editors=self.user) | Q(viewers=self.user))
        return experiments

    def get_context_data(self, **kwargs):
        ctx = {'active_tab': self.active_tab}
        lab = self.kwargs['lab_pk']
        experiments = self.get_experiments().values_list('pk', 'title')
        if 'experiment_pk' in self.kwargs:
            ctx['experiment'] = Experiment.objects.get(pk=self.kwargs.get('experiment_pk'))
        units = Unit.objects.filter(lab=lab, active=True).values_list('pk', 'sample')
        tags = Tag.objects.filter(lab=lab)
        ctx['column'] = json.dumps([
            {'editor': 'text', 'display': 'none'},
            {},
            {
                'editor': 'multi-select', 'selectOptions': [[unicode(e[0]), e[1]] for e in experiments],
                # 'validator_string': u'|'.join([e[1] for e in experiments]), 'allowInvalid': True
            },
            {'editor': 'multi-select', 'selectOptions': [[unicode(e[0]), e[1]] for e in units],
             # 'validator_string': '[%s]*' % u'|'.join([e[1] for e in units]), 'allowInvalid': True
            },
            {'editor': 'jstree', 'selectOptions': self.get_jstree_data(tags), 'renderer': 'renderTags'},
            # {'editor': 'text'},
            {'editor': 'text', 'display': 'none', 'readonly': True},
            {'editor': 'text'},
            {'editor': 'text', 'display': 'none'},
            {'editor': 'text', 'display': 'none'},
            {'editor': 'text', 'display': 'none'},
        ])
        ctx['title'] = json.dumps(dict(zip(self.title_fields + self.extra_title, self.headers)))
        ctx['headers'] = json.dumps(self.headers)
        # ctx['is_member'] = bool(filter(lambda x: x[self.headers.index('readonly')], units_list) or len(experiments))
        ctx['is_member'] = bool(len(experiments))
        return ctx


#
# class UnitCreateView(LoginRequiredMixin, RecentActivityMixin, DataMixin, AjaxableResponseMixin,
#                      JsTreeMixin, ModelFormMixin, MultipleObjectTemplateResponseMixin, BaseListView, View):
#     """
#      View for creating a new unit
#     """
#     model = Unit
#     form_class = UnitForm
#     update_form_class = UnitUpdateForm
#     template_name = 'units/unit_list.html'
#     active_tab = 'units'
#     title = {
#         'pk': 'pk', 'sample': 'sample', 'experiments_pk': 'experiments', 'parent_pk': 'parent', 'tags_pk': 'tags',
#         'change reasons': 'comment',
#     }
#     title_fields = ['pk', 'sample', 'experiments', 'parent', 'tags', 'readonly']
#     extra_title = ['change reasons', 'experiments_pk', 'parent_pk', 'tags_pk']
#     headers = ['pk', ugettext('sample'), ugettext('experiments'), ugettext('parents'), ugettext('tags'), 'readonly',
#                ugettext('change reasons'), 'experiments_pk', 'parent_pk', 'tags_pk']
#
#     @method_decorator(get_obj_or_404)
#     def form_valid(self, form):
#         self.object = form.save(commit=False)
#         self.object.lab = self.lab
#         user = self.request.user
#         if not (self.object.is_member(user) or self.object.is_owner(user)):
#             return {'errors': {'non_field_error': 'Permission denied'}, 'success': False}
#         self.object = self.object.save(user=self.request.user, revision_comment=form.cleaned_data.get('comment'))
#         self.save_recent_activity(self.flag, unit=self.object.pk,
#                                   experiment=[unicode(obj.pk) for obj in self.object.experiments])
#         return {'pk': unicode(self.object.pk), 'success': True}
#
#     @method_decorator(login_required)
#     @method_decorator(get_obj_or_404)
#     def dispatch(self, *args, **kwargs):
#         self.user = self.request.user
#         self.lab = Lab.objects.get(pk=self.kwargs.get('lab_pk'))
#         if not self.lab.is_assistant(self.request.user):
#             raise PermissionDenied
#         return super(UnitCreateView, self).dispatch(*args, **kwargs)
#
#     # def get_units(self):
#     #     """
#     #     Filter units depending on user's permission
#     #     """
#     #     self.user = self.request.user
#     #     if self.kwargs.get('experiment_pk'):
#     #         experiments = [self.kwargs.get('experiment_pk')]
#     #     else:
#     #         experiments = self.get_experiments().values_list('id')
#     #     self.object_list = self.object_list.filter(lab=self.lab, experiments__in=experiments, active=True)
#     #     queryset = []
#     #     for unit in self.object_list:
#     #         if unit.is_assistant(self.user):
#     #             record = []
#     #             for field in self.title_fields[:-1]:
#     #                 if hasattr(unit, field):
#     #                     field_data = getattr(unit, field, None)
#     #                     if field_data.__class__.__name__ == 'ManyRelatedManager':
#     #                         field_data = field_data.all()
#     #                         field_data = serializers.serialize('json', field_data)
#     #                     record.append(field_data)
#     #             record.append(unit.is_member(self.user) or unit.is_owner(self.user))
#     #             queryset.append(JsonDocumentEncoder(fields=self.title_fields,
#     #                                                 extra_fields=self.extra_title).encode_object(record))
#     #     return queryset
#
#     def get_experiments(self):
#         experiments = Experiment.objects.filter(lab=self.lab, active=True)
#         if self.lab.is_guest(self.user):
#             experiments = experiments.filter(Q(owners=self.user) | Q(editors=self.user) | Q(viewers=self.user))
#         return experiments
#
#     def get_context_data(self, **kwargs):
#         ctx = {'active_tab': self.active_tab}
#         # units_list = self.get_units()
#         # print(units_list)
#         # ctx['data'] = json.dumps(units_list)
#
#         lab = self.kwargs['lab_pk']
#         experiments = self.get_experiments().values_list('pk', 'title')
#         if 'experiment_pk' in self.kwargs:
#             ctx['experiment'] = Experiment.objects.get(pk=self.kwargs.get('experiment_pk'))
#         units = Unit.objects.filter(lab=lab, active=True).values_list('pk', 'sample')
#         tags = Tag.objects.filter(lab=lab)
#         ctx['column'] = json.dumps([
#             {'editor': 'text', 'display': 'none'},
#             {},
#             {
#                 'editor': 'multi-select', 'selectOptions': [[unicode(e[0]), e[1]] for e in experiments],
#                 # 'validator_string': u'|'.join([e[1] for e in experiments]), 'allowInvalid': True
#             },
#             {'editor': 'multi-select', 'selectOptions': [[unicode(e[0]), e[1]] for e in units],
#              # 'validator_string': '[%s]*' % u'|'.join([e[1] for e in units]), 'allowInvalid': True
#             },
#             {'editor': 'jstree', 'selectOptions': self.get_jstree_data(tags), 'renderer': 'renderTags'},
#             # {'editor': 'text'},
#             {'editor': 'text', 'display': 'none', 'readonly': True},
#             {'editor': 'text'},
#             {'editor': 'text', 'display': 'none'},
#             {'editor': 'text', 'display': 'none'},
#             {'editor': 'text', 'display': 'none'},
#         ])
#         ctx['title'] = json.dumps(dict(zip(self.title_fields + self.extra_title, self.headers)))
#         ctx['headers'] = json.dumps(self.headers)
#         # ctx['is_member'] = bool(filter(lambda x: x[self.headers.index('readonly')], units_list) or len(experiments))
#         ctx['is_member'] = bool(len(experiments))
#         return ctx
#

class UnitUpdateView(UnitCreateView):
    """
     View for update unit. Same as create,but is added description
     """
    title = {
        'pk': 'pk', 'sample': 'sample', 'experiments_pk': 'experiments', 'parent_pk': 'parent', 'tags_pk': 'tags',
        'change reasons': 'comment', 'description': 'description',
    }


class UnitDeleteView(LoginRequiredMixin, RecentActivityMixin, ActiveTabMixin, AjaxableResponseMixin, View):
    """
    View for removing an existing unit
    """
    model = Unit
    active_tab = 'units'

    def post(self, request, *args, **kwargs):
        ids = self.request.POST.get('data', '').split(',')
        removed = []
        for pk in ids:
            try:
                self.object = self.model.objects.get(pk=pk)
                if not self.object.is_owner(self.request.user):
                    removed.append({'errors': {'non_field_error': 'Permission denied'}, 'success': False})
                else:
                    self.object.active = False
                    # self.object.save(user=self.request.user)
                    self.object.save()
                    # Collection.objects.update(pull__units=self.object)
                    self.save_recent_activity(RecentActivity.DELETE, unit=pk,
                                              experiment=[unicode(obj.pk) for obj in self.object.experiments.all()])
                    removed.append(pk)
            except self.model.DoesNotExist:
                pass
        return self.render_to_json_response({'data': removed, 'success': True})


class UnitDeleteOneView(LoginRequiredMixin, RecentActivityMixin, ActiveTabMixin, DeleteView):
    """
    View for removing an existing unit
    """
    model = Unit
    active_tab = 'units'

    def delete(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        self.object = self.model.objects.get(pk=pk)
        if not self.object.is_owner(self.request.user):
            raise PermissionDenied
        self.object.active = False
        self.object.save()
        # self.object.save(user=self.request.user)
        self.save_recent_activity(RecentActivity.DELETE, unit=pk,
                                  experiment=[unicode(obj.pk) for obj in self.object.experiments.all()])
        self.get_success_message()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('units:list', kwargs={'lab_pk': self.kwargs.get('lab_pk')})

    def get_success_message(self):
        return messages.add_message(self.request, messages.SUCCESS, _('Unit was removed successfully.'))


class UnitDetailView(LoginRequiredMixin, CheckViewPermissionMixin, InitialLabMixin, RecentActivityMixin, ActiveTabMixin,
                     CommentMixin, UpdateView):
    """
    View for display information about an existing unit
    """
    model = Unit
    form_class = UnitTabForm
    template_name = 'units/unit_detail.html'
    active_tab = 'units'

    def get_object(self, queryset=None):
        unit = super(UnitDetailView, self).get_object(queryset)
        if not unit.is_assistant(self.request.user):
            raise PermissionDenied
        return unit

    def post(self, request, *args, **kwargs):
        response = super(UnitDetailView, self).post(request, *args, **kwargs)
        if not (self.object.is_member(request.user) or self.object.is_owner(request.user)):
            raise PermissionDenied
        return response

    def form_valid(self, form):
        self.object = form.save(commit=False)
        # self.object.save(user=self.request.user)
        self.object.save()
        self.save_recent_activity(RecentActivity.UPDATE, unit=self.object.pk, experiment=[unicode(obj.pk) for obj in self.object.experiments.all()])
        self.get_success_message()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_message(self):
        return messages.add_message(self.request, messages.SUCCESS, _('Unit was updated successfully.'))

    def get_context_data(self, **kwargs):
        ctx = super(UnitDetailView, self).get_context_data(**kwargs)
        ctx['measurements'] = self.get_measurement()
        return ctx

    def get_measurement(self):
        return self.object.measurement
        # result = self.model._get_collection().aggregate([
        #     {'$unwind': "$measurements"},
        #     {'$match': {'$and': [{'measurements.active': True}, {'_id': ObjectId(self.kwargs.get('pk'))}]}},
        #     {'$group': {
        #         '_id': {
        #             'measurement_type': "$measurements.measurement_type"
        #         },
        #         'values': {'$push': {
        #             'date': {
        #                 'year': {'$year': '$measurements.created_at'},
        #                 'month': {'$month': '$measurements.created_at'},
        #                 'day': {'$dayOfMonth': '$measurements.created_at'},
        #                 'hour': {'$hour': '$measurements.created_at'},
        #                 'minute': {'$minute': '$measurements.created_at'}
        #             },
        #             'value': "$measurements.value",
        #             'pk': "$measurements._id"
        #         }}
        #     }},
        # ])
        # for row in result['result']:
        #     row['measurement_type'] = MeasurementType.objects.get(pk=row['_id']['measurement_type'])
        # if result['result']:
        #     result['result'][0]['active'] = True
        # return result['result']


class UnitDetailJSONView(LoginRequiredMixin, CheckViewPermissionMixin, JsTreeMixin, InitialLabMixin,
                         RecentActivityMixin, ActiveTabMixin, CommentMixin, AjaxableResponseMixin, DetailView):
    """
    View for return json information about an existing unit(is used on experiment page)
    """
    model = Unit
    template_name = 'units/unit_detail.html'
    active_tab = 'units'

    def get_object(self, queryset=None, *args, **kwargs):
        unit = super(UnitDetailJSONView, self).get_object(queryset)
        return unit

    @method_decorator(login_required)
    @method_decorator(get_obj_or_404)
    def dispatch(self, *args, **kwargs):
        self.lab = Lab.objects.get(pk=self.kwargs.get('lab_pk'))
        if not self.lab.is_assistant(self.request.user):
            raise PermissionDenied
        return super(UnitDetailJSONView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if not (self.object.is_member(request.user) or self.object.is_owner(request.user)):
            raise PermissionDenied

        context = self.get_context_data()
        ctx = {}
        ctx.update(self.kwargs)

        if self.object.measurements:
            measurements = self.object.measurements.all().as_table()
        else:
            measurements = [
                ['', ''], ['', '']
            ]

        ctx['measurements'] = json.dumps(measurements)
        if self.object.measurements:
            ctx['revisions'] = json.dumps([self.rev_as_json(rev) for rev in self.object.measurements.revisions()])

        ctx['sample'] = self.object.sample
        # ctx['unit_data'] = self.object.to_json()
        # ctx['unit_data'] = json.dumps(self.object)
        ctx['unit_data'] = json.dumps(serialize(self.object, fields=['id', 'sample', 'experiments', 'lab', 'parent', 'tags'],
                                                 related={'parent': {'fields': ['id'], 'merge': True},
                                                          'experiments': {'fields': ['id'], 'merge': True},
                                                          'lab': {'fields': ['id'], 'merge': True},
                                                          'tags': {'fields': ['id'], 'merge': True}
                                                 }))
        # and now dump to JSON
        # ctx['unit_data'] = json.dumps(actual_data)
        ctx['tags'] = json.dumps(self.get_tree_element(self.object))

        ctx['description'] = render_to_string('units/tabs/unit_description.html', context)
        ctx['comments'] = render_to_string('units/tabs/unit_comments.html', context)

        return self.render_to_json_response(ctx)

    def get_tree_element(self, object, fields=('id', 'parent', 'details'), parent_id='#'):
        tags = object.tags
        tags_tree = self.get_jstree_data(tags, fields, parent_id=parent_id)
        return tags_tree

    def rev_as_json(self, revision):
        return {
            'timestamp': formats.date_format(revision.timestamp, 'DATETIME_FORMAT'),
            'pk': str(revision.pk),
            'url': reverse('measurements:measurement-revert', kwargs={'lab_pk': self.object.lab.pk, 'unit_pk': self.object.id, 'revision_pk': revision.pk}),
        }

    def get_context_data(self, **kwargs):
        ctx = super(UnitDetailJSONView, self).get_context_data(**kwargs)
        ctx['lab'] = self.lab
        ctx['lab_pk'] = self.lab.pk
        ctx['user'] = self.request.user
        # ctx['measurements'] = self.object.measurements
        ctx['form'] = UnitTabForm(lab_pk=self.lab.pk, instance=self.object)

        return ctx


class UnitFileUploadView(FileUploadMixinView):
    model = UnitFile
    parent_model= Unit


class UnitFileDropboxUploadView(DropboxFileUploadMixinView):
    model = UnitFile
    parent_model = Unit


class UnitFileLocalUploadView(LocalFileUploadMixinView):
    model = UnitFile
    parent_model = Unit


class CreateLinkView(LoginRequiredMixin, CheckViewPermissionMixin, InitialLabMixin,
                     AjaxableResponseMixin, SingleObjectMixin, View):
    model = Unit

    def post(self, request, *args, **kwargs):
        """
        Create new link attached to unit. Return html of preview box.
        """
        link = request.POST.get('link')
        try:
            link_info = self.get_info(link)
        except Exception as e:
            logger.error('Error in link preview', exc_info=True)
            link_info = {}

        unit_link = UnitLink.objects.create(
            parent=self.get_object(),
            link=link,
            title=link_info.get('title', ''),
            description=link_info.get('description', ''),
            image=link_info.get('image', ''),
        )

        lab_pk = kwargs.get('lab_pk')
        ctx = {
            'lab_pk': lab_pk,
            'link': unit_link,
        }
        return self.render_to_json_response({
            'pk': unicode(unit_link.pk),
            'success': True,
            'html': render_to_string('units/tabs/link.html', ctx)
        })

    def get_info(self, url):
        """
        Get html of url
        :param url: (string) url to parse
        :return: (dict) dict with title, description, image and canonical url
        """
        r = requests.get(url)
        html = bs4.BeautifulSoup(r.text)

        # first try open graph
        try:
            title = html.find("meta", {"name": "og:title"}).get('content', '')
        except AttributeError:
            title = None
        try:
            description = html.find("meta", {"property": "og:description"}).get('content', '')
        except AttributeError:
            description = None
        try:
            image = html.find("meta", {"property": "og:image"}).get('content', '')
        except AttributeError:
            image = None

        # then meta
        if not title:
            try:
                title = html.title.text
            except AttributeError:
                title = None
        if not description:
            try:
                description = html.find("meta", {"name": "description"}).get('content', '')
            except AttributeError:
                description = None

        # another images
        if not image:
            try:
                image = html.find("link", {"rel": "icon"}).get('href', '')
            except AttributeError:
                image = None
        if not image:
            try:
                image = html.find('img').get('src', '')
            except AttributeError:
                image = None

        if image:
            image = self.to_full_url(image, url)

        # If there isn't description get first paragraph
        if not description:
            try:
                description = html.find("p").text[:70] + u' ...'
            except AttributeError:
                description = None
        try:
            canonical = html.find("link", {"rel": "canonical"}).get('href', '')
        except AttributeError:
            canonical = url

        result = {
            'title': title,
            'image': image,
            'url': url,
            'canonicalUrl': canonical,
            'description': u'{}'.format(description),
        }

        return result

    def to_full_url(self, url, parent_url):
        """
        Handle url of image. Add domain if url is relative
        :param url: (string) url of image or another resource. Relative or absolute
        :param parent_url: (string) Url of requested parent page
        :return: Full url to image
        """
        if url.startswith('http://') or url.startswith('https://'):
            return url

        parsed_url = urlparse(parent_url)
        if url.startswith('/'):
            return parsed_url.scheme + '://' + parsed_url.netloc + url
        else:
            path = parsed_url.path.split('/')[:-1]
            path = '/'.join(path)
            return parsed_url.scheme + '://' + parsed_url.netloc + path + '/' + url


class DeleteLinkView(LoginRequiredMixin, CheckViewPermissionMixin, AjaxableResponseMixin, DeleteView):
    model = UnitLink

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return self.render_to_json_response({'success': True})