# -*- coding: utf-8 -*-
import json
import bs4
import requests
from urlparse import urlparse

from django.utils.decorators import method_decorator
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.db.models import Q

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from reversion import revisions as reversion

from common.mixins import LoginRequiredMixin, AjaxableResponseMixin, CheckLabPermissionMixin, RecentActivityMixin
from dashboard.models import RecentActivity
from units.api.serializers import UnitSerializer, UnitTableSerializer,UnitLinkSerializer
from units.models import Unit, UnitLink
from experiments.models import Experiment
from labs.models import Lab


class UnitListView(LoginRequiredMixin, CheckLabPermissionMixin, generics.ListAPIView):

    serializer_class = UnitTableSerializer

    def get_queryset(self, **kwargs):
        if self.kwargs.get('experiment_pk'):
            experiments = [self.kwargs.get('experiment_pk')]
        else:
            experiments = Experiment.objects.filter(lab=self.lab, active=True)
            if self.lab.is_guest(self.request.user):
                experiments = experiments.filter(Q(owners=self.user) | Q(editors=self.user) | Q(viewers=self.user))
            experiments = experiments.values_list('id')
        return Unit.objects.filter(lab__pk=self.kwargs['lab_pk'], experiments__in=experiments, active=True)


class UnitTableView(LoginRequiredMixin, CheckLabPermissionMixin, RecentActivityMixin, AjaxableResponseMixin, View):

    serializer_class = UnitTableSerializer

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(UnitTableView, self).dispatch(*args, **kwargs)

    def post(self, *args, **kwargs):
        results = []
        for index, unit_data in enumerate(json.loads(self.request.body)):
            if not unit_data:
                continue
            if 'lab' not in unit_data:
                unit_data['lab'] = self.lab.pk

            # check permission
            permission = False
            for experiment in Experiment.objects.filter(pk__in=unit_data.get('experiments', [])):
                if experiment.is_owner(self.request.user) or experiment.is_editor(self.request.user):
                    permission = True
                    break

            if not (self.lab.is_owner(self.request.user) or permission):
                results.append({'errors': {'non_field_error': 'Permission denied'}, 'success': False})
                continue

            try:
                if unit_data.get('pk', None):
                    unit = Unit.objects.get(pk=unit_data['pk'])
                    serializer = self.serializer_class(unit, data=unit_data)
                    self.flag = RecentActivity.UPDATE
                else:
                    raise Unit.DoesNotExist
            except Unit.DoesNotExist:
                serializer = self.serializer_class(data=unit_data)
                self.flag = RecentActivity.ADD

            if serializer.is_valid():
                with reversion.create_revision():
                    unit = serializer.save()
                    reversion.set_user(self.request.user)
                    reversion.set_comment(serializer.data.get('change_reasons', ''))
                    self.save_recent_activity(self.flag, obj=unit)
                    results.append((index, {'pk': unit.pk, 'success': True}))
            else:
                results.append((index, {'errors': serializer.errors, 'success': False}))
        return self.render_to_json_response(results)

    def get_queryset(self, **kwargs):
        return Unit.objects.filter(lab__pk=self.kwargs['lab_pk'])


class UnitCreateView(LoginRequiredMixin, CheckLabPermissionMixin, generics.ListCreateAPIView):
    def get_queryset(self, **kwargs):
        if self.request.GET.get('experiment_pk'):
            experiments = [self.request.GET.get('experiment_pk')]
        else:
            experiments = Experiment.objects.filter(lab=self.lab, active=True)
            if self.lab.is_guest(self.request.user):
                experiments = experiments.filter(Q(owners=self.user) | Q(editors=self.user) | Q(viewers=self.user))
            experiments = experiments.values_list('id')
        return Unit.objects.filter(lab__pk=self.kwargs['lab_pk'], experiments__in=experiments, active=True)
    serializer_class = UnitSerializer


class UnitUpdateView(LoginRequiredMixin, CheckLabPermissionMixin, generics.RetrieveUpdateDestroyAPIView):

    serializer_class = UnitSerializer

    def get_queryset(self, **kwargs):
        if self.kwargs.get('experiment_pk'):
            experiments = [self.kwargs.get('experiment_pk')]
        else:
            experiments = Experiment.objects.filter(lab=self.lab, active=True)
            if self.lab.is_guest(self.request.user):
                experiments = experiments.filter(Q(owners=self.user) | Q(editors=self.user) | Q(viewers=self.user))
            experiments = experiments.values_list('id')
        return Unit.objects.filter(lab__pk=self.kwargs['lab_pk'], experiments__in=experiments, active=True)


class UnitLinkListView(LoginRequiredMixin, CheckLabPermissionMixin, generics.ListAPIView):

    serializer_class = UnitLinkSerializer

    def get_queryset(self, **kwargs):
        return UnitLink.objects.filter(parent__pk=self.kwargs.get('unit_pk'))


class UnitLinkDetailView(LoginRequiredMixin, CheckLabPermissionMixin, generics.RetrieveUpdateDestroyAPIView):

    serializer_class = UnitLinkSerializer
    queryset = UnitLink.objects.all()
    # TODO: permissions?


class UnitLinkCreateView(LoginRequiredMixin, generics.CreateAPIView):

    serializer_class = UnitLinkSerializer
    queryset = UnitLink.objects.all()

    def post(self, *args, **kwargs):
        request_data = json.loads(self.request.body)
        link = request_data.get('link')
        parent = request_data.get('parent')

        try:
            link_info = self.get_info(link)
        except Exception as e:
            # logger.error('Error in link preview', exc_info=True)
            link_info = {}

        unit_link = UnitLink.objects.create(
            parent=Unit.objects.get(pk=parent),
            link=link,
            title=link_info.get('title', ''),
            description=link_info.get('description', ''),
            image=link_info.get('image', ''),
        )

        serializer = self.get_serializer(unit_link)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

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