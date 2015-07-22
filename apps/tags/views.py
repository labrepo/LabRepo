import json

from django.core.urlresolvers import reverse
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _

from common.decorators import get_obj_or_404
from common.mixins import (RecentActivityMixin, AjaxableResponseMixin, ActiveTabMixin, LoginRequiredMixin,
                           LabQueryMixin, JsTreeMixin, CheckLabPermissionMixin)
from dashboard.documents import RecentActivity
from .documents import Tag
from labs.documents import Lab
from tags.forms import TagForm
from units.documents import Unit


class TagCreateView(LoginRequiredMixin, CheckLabPermissionMixin, AjaxableResponseMixin, JsTreeMixin,
                    RecentActivityMixin, ActiveTabMixin, CreateView):
    """
     View for creating a new tag
    """
    model = Tag
    form_class = TagForm
    active_tab = 'tags'
    template_name = 'tags/tag_form.html'
    parent_id = '#'
    fields = ('id', 'parent', 'details')

    def get_initial(self):
        initial = super(TagCreateView, self).get_initial()
        initial['lab_pk'] = self.kwargs.get('lab_pk')
        if 'parent' in self.request.GET:
            initial['parent'] = self.request.GET.get('parent')
        return initial

    @method_decorator(get_obj_or_404)
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.lab = Lab.objects.get(pk=self.kwargs.get('lab_pk'))
        self.object.save()
        self.save_recent_activity(RecentActivity.ADD)
        return self.render_data(HttpResponseRedirect(self.get_success_url()))

    def render_data(self, response=None):
        if self.request.is_ajax():
            data = {'node': self.get_jstree_data([self.object], self.fields, self.parent_id),
                    'message': self.get_success_message()}
            return self.render_to_json_response(data)
        else:
            return response

    def get_success_url(self):
        return reverse('tags:list', kwargs={'lab_pk': self.kwargs.get('lab_pk')})

    def get_success_message(self):
        return _('Tag "{}" was created successfully.'.format(self.object.details))


class TagUpdateView(LoginRequiredMixin, CheckLabPermissionMixin, AjaxableResponseMixin, JsTreeMixin,
                    RecentActivityMixin, UpdateView):
    """
    View for updating an existing tag
    """
    model = Tag
    form_class = TagForm
    parent_id = '#'
    template_name = 'tags/tag_form.html'
    fields = ('id', 'parent', 'details')

    def get_initial(self):
        initial = super(TagUpdateView, self).get_initial()
        initial['lab_pk'] = self.kwargs.get('lab_pk')
        return initial

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.lab = Lab.objects.get(pk=self.kwargs.get('lab_pk'))
        self.object.save()
        self.save_recent_activity(RecentActivity.UPDATE)
        return self.render_data(HttpResponseRedirect(self.get_success_url()))

    def render_data(self, response=None):
        if self.request.is_ajax():
            data = {'node': self.get_jstree_data(self.object.get_children(), self.fields, self.parent_id),
                    'message': self.get_success_message()}
            return self.render_to_json_response(data)
        else:
            return response

    def get_success_message(self):
        return _('Tag "{}" was updated successfully.'.format(self.object.details))


class TagDeleteView(LoginRequiredMixin, CheckLabPermissionMixin, ActiveTabMixin, AjaxableResponseMixin,
                    RecentActivityMixin, DeleteView):
    """
    View for removing an existing tag
    """
    model = Tag
    active_tab = 'tags'
    template_name = 'tags/tag_form.html'

    def delete(self, request, *args, **kwargs):
        ids = request.POST.getlist('ids[]')
        object_list = self.model.objects.filter(lab=self.kwargs.get('lab_pk'), pk__in=ids)
        for obj in object_list:
            self.save_recent_activity(RecentActivity.DELETE, obj=obj)
        object_list.delete()
        Unit.objects.filter(tags__in=ids).update(pull_all__tags=ids)
        return self.render_data(HttpResponseRedirect(self.get_success_url()))

    def render_data(self, response=None):
        if self.request.is_ajax():
            data = {'message': self.get_success_message()}
            return self.render_to_json_response(data)
        else:
            return response

    def get_success_url(self):
        return reverse('tags:list', kwargs={'lab_pk': self.kwargs.get('lab_pk')})

    def get_success_message(self):
        return _('Tag was removed successfully.')


class TagListView(LoginRequiredMixin, CheckLabPermissionMixin, LabQueryMixin, JsTreeMixin, ActiveTabMixin, ListView):
    """
    View for display list of existing tags
    """
    model = Tag
    template_name = 'tags/tag_list.html'
    active_tab = 'tags'
    form = TagForm

    def get_context_data(self, **kwargs):
        ctx = super(TagListView, self).get_context_data(**kwargs)
        ctx['tags'] = json.dumps(self.get_tree_element(self.model))
        ctx['form'] = TagForm(initial={'lab_pk': self.lab.pk, 'user': self.request.user})
        return ctx

    def get_tree_element(self, model, fields=('id', 'parent', 'details'), parent_id='#'):
        tags = model.objects.filter(lab=self.kwargs.get('lab_pk'))
        tags_tree = self.get_jstree_data(tags, fields, parent_id=parent_id)
        return tags_tree
