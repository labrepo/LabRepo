# -*- coding: utf-8 -*-
from django.core.exceptions import PermissionDenied
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.generic import CreateView, UpdateView, DeleteView

from comments.forms import CommentForm
from common.mixins import LoginRequiredMixin, AjaxableResponseMixin, RecentActivityMixin, CheckLabPermissionMixin, \
    InitialLabMixin

from dashboard.models import RecentActivity
from labs.models import Lab
from units.models import Unit
from experiments.models import Experiment
from comments.models import Comment


class CommentCreateView(CheckLabPermissionMixin, AjaxableResponseMixin, InitialLabMixin, RecentActivityMixin, CreateView):
    """
    View for create a comment.

    Note:
        Now is used only for unit comments. Comments for a experiment are created through API.
    """
    model = Comment
    form_class = CommentForm
    template_name = 'comments/comment_block.html'
    prefix = 'create'

    def form_valid(self, form):

        self.object = Comment(
            text=form.cleaned_data['text']
        )
        model_name = form.cleaned_data['instance_type']  # todo type__model
        if model_name == 'Experiment':
            model = Experiment
        if model_name == 'Unit':
            model = Unit
            experiment = None
        self.object.init_user = self.request.user
        self.object.content_object = model.objects.get(id=form.cleaned_data['object_id'])
        self.object.save()

        if model_name == 'Experiment':
            experiment = self.object.content_object

        self.save_recent_activity(RecentActivity.COMMENT,
                                  value=self.object.text,
                                  obj=self.object.content_object,
                                  experiment=experiment)

        return self.render_to_json_response({'data': render_to_string(self.template_name, {'comment': self.object},
                                                                      context_instance=RequestContext(self.request)),
                                             # 'resent_activity': render_to_string('dashboard/resent.html',
                                             #                                     {'object': resent_activity})
                                             })


class CommentUpdateView(CheckLabPermissionMixin, InitialLabMixin, AjaxableResponseMixin, UpdateView):
    """
    View for editing an existing comment
    """
    model = Comment
    form_class = CommentForm
    template_name = 'comments/comment_block.html'
    prefix = 'update'

    def get_object(self, queryset=None):
        obj = super(CommentUpdateView, self).get_object(queryset)
        user = self.request.user
        lab = Lab.objects.get(pk=self.kwargs['lab_pk'])
        if user in lab.investigator.all() or obj.init_user == user:
            return obj
        raise PermissionDenied

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if not self.object.init_user:
            self.object.init_user = self.request.user
        self.object.object_id = form.cleaned_data['object_id']
        self.object.save()
        return self.render_to_json_response(
            {'data': render_to_string(self.template_name,
                                      {'comment': self.object, 'lab': Lab.objects.get(pk=self.kwargs['lab_pk'])},
             context_instance=RequestContext(self.request)),
             'pk': unicode(self.object.pk)}
        )


class CommentDeleteView(LoginRequiredMixin, AjaxableResponseMixin, RecentActivityMixin, DeleteView):
    """
    View for removing an existing comment

    Note:
        Now is used only for unit comments. Comments for a experiment are handled through API.
    """
    model = Comment

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.save_recent_activity(RecentActivity.DELETE)
        self.object.delete()
        return self.render_to_json_response({'pk': unicode(self.object.pk)})

    def get_object(self, queryset=None):
        obj = super(CommentDeleteView, self).get_object(queryset)
        user = self.request.user
        lab = Lab.objects.get(pk=self.kwargs['lab_pk'])
        if user in lab.investigator.all() or obj.init_user == user:
            return obj
        raise PermissionDenied