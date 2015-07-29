import json
from bson import ObjectId

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.utils.decorators import method_decorator

from mongoengine import ListField, Document

from comments.documents import Comment
from comments.forms import CommentForm
from common.decorators import get_obj_or_404
from dashboard.documents import RecentActivity
from labs.documents import Lab
from profiles.forms import InviteUserForm


class LoginRequiredMixin(object):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


class CheckLabPermissionMixin(object):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.lab = Lab.objects.get(pk=self.kwargs.get('lab_pk'))
        if not self.lab.is_assistant(self.request.user):
            raise PermissionDenied
        return super(CheckLabPermissionMixin, self).dispatch(*args, **kwargs)


class CheckEditPermissionMixin(object):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        object = self.get_object()
        if not (object.is_owner(self.request.user) or object.is_member(self.request.user)):
            raise PermissionDenied
        return super(CheckEditPermissionMixin, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(CheckEditPermissionMixin, self).get_context_data(**kwargs)
        ctx['is_owner'] = self.object.is_owner(self.request.user)
        ctx['is_member'] = self.object.is_member(self.request.user)
        return ctx


class CheckDeletePermissionMixin(CheckEditPermissionMixin):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        object = self.get_object()
        if not object.is_owner(self.request.user):
            raise PermissionDenied
        return super(CheckDeletePermissionMixin, self).dispatch(*args, **kwargs)


class CheckViewPermissionMixin(object):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        object = self.get_object()
        if not object.is_assistant(self.request.user):
            raise PermissionDenied
        return super(CheckViewPermissionMixin, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):    # todo  into other mixin
        ctx = super(CheckViewPermissionMixin, self).get_context_data(**kwargs)
        ctx['is_owner'] = self.object.is_owner(self.request.user)
        ctx['is_member'] = self.object.is_member(self.request.user)
        return ctx


class FormInitialMixin(object):

    @method_decorator(get_obj_or_404)
    def get_initial(self):
        self.initial = {'lab': self.lab, 'user': self.request.user}
        return super(FormInitialMixin, self).get_initial()


class ActiveTabMixin(object):
    def get_context_data(self, **kwargs):
        ctx = super(ActiveTabMixin, self).get_context_data(**kwargs)
        ctx['active_tab'] = self.active_tab
        return ctx


class LabQueryMixin(object):
    def get_queryset(self):
        queryset = super(LabQueryMixin, self).get_queryset()
        return queryset.filter(lab=self.kwargs.get('lab_pk'))


class RecentActivityMixin(object):

    def save_recent_activity(self, action_flag, **kwargs):
        obj = kwargs.get('obj', getattr(self, 'object', None))
        kwargs['object_name'] = obj.__unicode__()
        if obj:
            return RecentActivity.objects.create(
                lab_id=self.kwargs.get('lab_pk'),
                init_user=self.request.user,
                instance_type=obj._meta.object_name,
                object_id=obj.pk,
                action_flag=action_flag,
                content_object=obj,
                extra=kwargs
            )


class InitialLabMixin(object):
    def get_form_kwargs(self):
        kwargs = super(InitialLabMixin, self).get_form_kwargs()
        kwargs['lab_pk'] = self.kwargs.get('lab_pk')
        return kwargs


class CommentMixin(object):

    def get_comment_initial(self):
        return {'instance_type': self.model._meta.object_name, 'object_id': self.object.pk}

    def get_list_comment(self):
        return Comment.objects.filter(instance_type=self.model._meta.object_name, object_id=self.object.pk)

    def get_context_data(self, **kwargs):
        ctx = super(CommentMixin, self).get_context_data(**kwargs)
        ctx['comment_form_create'] = CommentForm(initial=self.get_comment_initial(), lab_pk=self.kwargs.get('lab_pk'), prefix='create')
        ctx['comment_form_update'] = CommentForm(initial=self.get_comment_initial(), lab_pk=self.kwargs.get('lab_pk'), prefix='update')
        ctx['comments'] = self.get_list_comment()
        return ctx


class AjaxableResponseMixin(object):

    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """
    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return self.render_to_json_response(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        response = super(AjaxableResponseMixin, self).form_valid(form)
        return self.render_data(response)

    def render_data(self, response=None):
        if self.request.is_ajax():
            data = {'pk': unicode(self.object.pk), 'name': self.object.__unicode__()} if getattr(self, 'object', None) else {}
            return self.render_to_json_response(data)
        else:
            return response


class DataMixin(object):

    def get_data(self, data_list, i):
        data = {}
        for key in data_list.keys():
            if key.startswith("data-" + str(i) + '-'):
                k = key.replace("data-" + str(i) + '-', '').replace('[]', '').lower()
                if k in self.title:
                    if isinstance(getattr(self.model, self.title[k], None), ListField):
                        data[self.title[k]] = data_list.getlist(key)
                    else:
                        data[self.title[k]] = data_list[key]
        return data

    def is_changed(self, data):
        if self.object:
            for name in self.title.values():
                field = getattr(self.object, name, None)
                if not field is None:
                    if hasattr(field, '__iter__') and not isinstance(field, Document):
                        value = [unicode(getattr(v, 'pk', v)) for v in field]
                    elif isinstance(field, Document):
                        value = unicode(field.pk)
                    elif isinstance(field, ObjectId):
                        value = unicode(field)
                    else:
                        value = field
                    if (value or data.get(name)) and value != data.get(name):
                        return True
                else:
                    if data.get(name):
                        return True
            return False
        return True

    def get_object(self):
        if self.kwargs.get(self.pk_url_kwarg, None):
            try:
                obj = super(DataMixin, self).get_object()
            except self.model.DoesNotExist:
                obj = None
            self.flag = RecentActivity.UPDATE
            self.form = getattr(self, 'update_form_class', self.form_class)
            return obj
        self.flag = RecentActivity.ADD
        self.form = self.form_class

    def post(self, request, *args, **kwargs):
        # todo change it
        results = []
        data_list = self.request.POST
        self.lab = Lab.objects.get(pk=self.kwargs.get('lab_pk'))
        for i in range(int(data_list.get('length', 0))):
            data = self.get_data(data_list, i)
            if data:
                self.kwargs['pk'] = data.get('pk', None)
                self.object = self.get_object()
                #TODO: remove descriptio
                if getattr(self.object, 'description', '') and not 'description' in self.title:
                    data['description'] = self.object.description

                form = self.form(data=data, instance=self.object, lab_pk=self.kwargs.get('lab_pk'))
                if self.is_changed(data):
                    user = request.user
                    if self.object and not (self.object.is_member(user) or self.object.is_owner(user)):
                        results.append((i, {'errors': {'non_field_error': 'Permission denied'}, 'success': False}))
                    if form.is_valid():
                        results.append((i, self.form_valid(form)))
                    else:
                        results.append((i, self.form_invalid(form)))
        return self.render_to_json_response(results)

    def form_invalid(self, form):
        return {'success': False, 'errors': form.errors}

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.lab = self.lab
        self.object.save()
        self.save_recent_activity(self.flag)
        return {'pk': unicode(self.object.pk), 'success': True}


class DeleteDataMixin(object):

    def delete(self, request, *args, **kwargs):
        ids = self.request.POST.get('data', '').split(',')
        removed = []
        for pk in ids:
            try:
                self.object = self.model.objects.get(pk=pk)
                self.object.active = False
                self.object.save()
                self.save_recent_activity(RecentActivity.DELETE, **{self.model._meta.object_name.lower(): self.object.pk})
                removed.append(pk)
            except self.model.DoesNotExist:
                pass
        return self.render_to_json_response({'data': removed, 'success': True})


class InviteFormMixin(object):
    def get_context_data(self, **kwargs):
        ctx = super(InviteFormMixin, self).get_context_data(**kwargs)
        ctx['extra_form'] = InviteUserForm()
        return ctx


class JsTreeMixin(object):

    def get_jstree_data(self, object_list, fields=('id', 'parent', 'details'), parent_id='#'):
        result = []
        for obj in object_list:
            data = dict(zip(['id', 'parent', 'text'], map(lambda x: getattr(obj, x), fields)))
            data['parent'] = unicode(getattr(data['parent'], 'id', parent_id))
            data['id'] = unicode(data['id'])
            data['a_attr'] = {'href': obj.get_absolute_url()}
            if hasattr(obj, 'color'):
                data['a_attr']['style'] = 'color: {}'.format(obj.color or '#000000')
            data['icon'] = False
            result.append(data.copy())
        return result

    def get_fancytree_data(self, object_list):
        result = []

        def get_tag_data(tag, tags):
            data = {'key': unicode(tag.id), 'title': tag.details}
            children = [get_tag_data(t, tags) for t in tags if t.parent == tag]
            if children:
                data['children'] = children
            return data

        for obj in object_list:
            if not obj.parent:
                result.append(get_tag_data(obj, object_list))
        return result




        #         data = dict(zip(['id', 'parent', 'text'], map(lambda x: getattr(obj, x), fields)))
        #     data = dict(zip(['id', 'parent', 'text'], map(lambda x: getattr(obj, x), fields)))
        #     data['parent'] = unicode(getattr(data['parent'], 'id', parent_id))
        #     data['id'] = unicode(data['id'])
        #     data['a_attr'] = {'href': obj.get_absolute_url()}
        #     if hasattr(obj, 'color'):
        #         data['a_attr']['style'] = 'color: {}'.format(obj.color or '#000000')
        #     data['icon'] = False
        #     result.append(data.copy())
        # return result