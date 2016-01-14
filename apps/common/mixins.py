import json
from bson import ObjectId

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.contrib.contenttypes.models import ContentType

from comments.models import Comment
from comments.forms import CommentForm
from common.decorators import get_obj_or_404
from dashboard.models import RecentActivity
from labs.models import Lab
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

    def save_recent_activity(self, action_flag,  **kwargs):
        obj = kwargs.get('obj', getattr(self, 'object', None))
        kwargs['object_name'] = obj.__unicode__()
        if obj:
            ra = RecentActivity.objects.create(
                lab_id=Lab.objects.get(pk=self.kwargs.get('lab_pk')),
                init_user=self.request.user,
                content_object=obj,
                action_flag=action_flag,
                value=kwargs.get('value', None),
            )
            if kwargs.get('experiment', None):
                experiments = kwargs.get('experiment', None)
                if type(experiments) is not list:
                    experiments = [experiments]
                for exp in experiments:
                    ra.experiments.add(exp)
            return ra


class InitialLabMixin(object):
    def get_form_kwargs(self):
        kwargs = super(InitialLabMixin, self).get_form_kwargs()
        kwargs['lab_pk'] = self.kwargs.get('lab_pk')
        return kwargs


class CommentMixin(object):

    def get_comment_initial(self):
        return {'instance_type': self.model._meta.object_name, 'object_id': self.object.pk}

    def get_list_comment(self):
        content_type = ContentType.objects.get_for_model(self.model)
        return Comment.objects.filter(instance_type=content_type, object_id=self.object.pk).order_by('action_time')

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


class InviteFormMixin(object):
    def get_context_data(self, **kwargs):
        ctx = super(InviteFormMixin, self).get_context_data(**kwargs)
        ctx['extra_form'] = InviteUserForm()
        return ctx


class JsTreeMixin(object):

    def get_jstree_data(self, object_list, fields=('id', 'parent', 'details'), parent_id='#'):
        result = []
        for obj in object_list.all():
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