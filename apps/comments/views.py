# -*- coding: utf-8 -*-

from django.core.exceptions import PermissionDenied
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.generic import CreateView, UpdateView, DeleteView

from comments.forms import CommentForm
from common.mixins import LoginRequiredMixin, AjaxableResponseMixin, RecentActivityMixin, CheckLabPermissionMixin, \
    InitialLabMixin
from dashboard.documents import RecentActivity
from .documents import Comment
from labs.documents import Lab


class CommentCreateView(CheckLabPermissionMixin, AjaxableResponseMixin, InitialLabMixin, RecentActivityMixin, CreateView):
    """
    View for create comment
    """
    model = Comment
    form_class = CommentForm
    template_name = 'comments/comment.html'
    prefix = 'create'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.init_user = self.request.user
        self.object.object_id = form.cleaned_data['object_id']
        self.object.save()
        resent_activity = self.save_recent_activity(RecentActivity.COMMENT,
                                                    **{'comment_model': self.object.instance_type,
                                                    self.object.instance_type.lower(): self.object.object_id})
        return self.render_to_json_response({'data': render_to_string(self.template_name, {'comment': self.object},
                                                                      context_instance=RequestContext(self.request)),
                                             'resent_activity': render_to_string('dashboard/resent.html',
                                                                                 {'object': resent_activity})})


class CommentUpdateView(CheckLabPermissionMixin, InitialLabMixin, AjaxableResponseMixin, UpdateView):
    """
    View for editing an existing comment
    """
    model = Comment
    form_class = CommentForm
    template_name = 'comments/comment.html'
    prefix = 'update'

    def get_object(self, queryset=None):
        obj = super(CommentUpdateView, self).get_object(queryset)
        user = self.request.user
        lab = Lab.objects.get(pk=self.kwargs['lab_pk'])
        if user in lab.investigator or obj.init_user == user:
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
    """
    model = Comment

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        self.save_recent_activity(RecentActivity.DELETE, comment_model=self.object.instance_type)
        return self.render_to_json_response({'pk': unicode(self.object.pk)})

    def get_object(self, queryset=None):
        obj = super(CommentDeleteView, self).get_object(queryset)
        user = self.request.user
        lab = Lab.objects.get(pk=self.kwargs['lab_pk'])
        if user in lab.investigator or obj.init_user == user:
            return obj
        raise PermissionDenied